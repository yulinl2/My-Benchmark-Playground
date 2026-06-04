/**
 * Gmail -> Claude Code Routine bridge.
 *
 * Polls a Gmail label and fires a routine's /fire endpoint with the email body
 * as `text`. No domain or server needed — runs on Google's infra.
 *
 * Setup:
 *   1. Project Settings -> Script properties:
 *        ROUTINE_TOKEN = sk-ant-oat01-...   (the token shown once when you
 *                                            generated the API trigger)
 *   2. Set FIRE_URL below to your routine's /fire URL.
 *   3. Triggers -> add a time-driven trigger on `poll`, every 1 minute.
 *   4. Gmail -> create a filter that labels trusted task mail `claude-task`.
 *
 * Only mail under the `claude-task` label is read, and it is marked read after
 * firing so it is not sent twice. Keep the label's filter tight: the routine
 * acts autonomously on whatever text you forward.
 */

const FIRE_URL =
  'https://api.anthropic.com/v1/claude_code/routines/REPLACE_WITH_trig_id/fire';
const LABEL = 'claude-task';

function poll() {
  const token = PropertiesService.getScriptProperties().getProperty('ROUTINE_TOKEN');
  if (!token) throw new Error('Set ROUTINE_TOKEN in Script properties.');

  const threads = GmailApp.search('label:' + LABEL + ' is:unread');
  for (const thread of threads) {
    const msg = thread.getMessages()[thread.getMessageCount() - 1];
    const text =
      'From: ' + msg.getFrom() + '\n' +
      'Subject: ' + msg.getSubject() + '\n\n' +
      msg.getPlainBody().slice(0, 60000); // /fire `text` is freeform, not parsed

    const res = UrlFetchApp.fetch(FIRE_URL, {
      method: 'post',
      contentType: 'application/json',
      muteHttpExceptions: true,
      headers: {
        Authorization: 'Bearer ' + token,
        'anthropic-beta': 'experimental-cc-routine-2026-04-01',
        'anthropic-version': '2023-06-01',
      },
      payload: JSON.stringify({ text: text }),
    });

    const code = res.getResponseCode();
    if (code >= 200 && code < 300) {
      thread.markRead();
      const url = (JSON.parse(res.getContentText()) || {}).claude_code_session_url;
      Logger.log('Fired: ' + url);
    } else {
      // Leave unread so the next poll retries; inspect the log on repeated failure.
      Logger.log('Fire failed (' + code + '): ' + res.getContentText());
    }
  }
}
