# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Load the antigen plugin manager
source ~/.local/lib/antigen.zsh

antigen use ohmyzsh/ohmyzsh

# Oh-my-zsh bundled plugins
antigen bundle git
antigen bundle brew
antigen bundle gh
antigen bundle macos
antigen bundle colored-man-pages
antigen bundle extract

# fzf-tab: must load AFTER compinit but BEFORE autosuggestions/syntax-highlighting
antigen bundle Aloxaf/fzf-tab

# Wrapping plugins
antigen bundle zsh-users/zsh-autosuggestions
antigen bundle zsh-users/zsh-syntax-highlighting

# history-substring-search: must load AFTER syntax-highlighting
antigen bundle zsh-users/zsh-history-substring-search

antigen theme romkatv/powerlevel10k #Sets prompt
antigen apply #Applies changes

# Bind arrow keys for history-substring-search
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Source aliases — organized by topic under aliases/. Auto-picks up any new file
# (general, git, media, gmail, ...). Add a new file in aliases/ and it'll just work.
for f in ~/Developer/mac-dotfiles/aliases/*; do
    [ -f "$f" ] && source "$f"
done

. "$HOME/.cargo/env"

# Relocate Python REPL history out of ~ (Python 3.13+ uses PYTHON_HISTORY; 3.9 needs this shim)
export PYTHONSTARTUP="$HOME/.config/python/pythonrc"
