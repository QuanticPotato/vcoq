let s:current_dir=expand("<sfile>:p:h")
py import sys, vim
py if not vim.eval("s:current_dir") in sys.path:
	\  sys.path.append(vim.eval("s:current_dir"))
py import vcoq

" User commands and mappings

function! LaunchC() 
	py vcoq.main.launch()
endfunction

function! Next()
	py vcoq.main.next()
endfunction

function! Prev()
	py vcoq.main.prev()
endfunction

" Write current buffers to a file
function! Write(filename)
	call pyeval('vcoq.main.onWrite("' . a:filename . '")')
endfunction
command! -nargs=1 W call Write(<f-args>)

" Open a file in the Edit buffer
function! Open(filename)
	call pyeval('vcoq.main.onOpen("' . a:filename . '")')
endfunction
command! -nargs=1 O call Open(<f-args>)

map <F9> :call LaunchC()<CR>

function! MapVcoq()
	" WARNING : 	imaps.vim already use the <c-j> map. To avoid any conflicts,
	" 		we first unmap this key sequence (You might want to change
	" 		it if <c-j> is already in use in another plugin)
	unmap <c-j>
	map <c-j>  :call Next()<CR>
	imap <c-j> <Esc>:call Next()<CR>a
	
	" Prev() map
	map <c-l> :call Prev()<CR>
	imap <c-l> <Esc>:call Prev()<CR>a
endfunction

function! SetupHighlights()
	highlight ErrorMessage ctermbg=Red ctermfg=White
	" The following highlights correspond to the python Color enum
	highlight Red ctermbg=Red ctermfg=White
	highlight Blue ctermbg=Blue ctermfg=White
	highlight Yellow ctermbg=Yellow ctermfg=Black
	highlight White ctermbg=White ctermfg=Black
	highlight Green ctermbg=Green ctermfg=White
	highlight Purple ctermbg=Magenta ctermfg=White
endfunction

call SetupHighlights()

autocmd BufEnter * call pyeval('vcoq.main.onBufferFocus(True, "' . expand('<afile>') . '")')
autocmd BufLeave * call pyeval('vcoq.main.onBufferFocus(False, "' . expand('<afile>') . '")')
"autocmd BufWinLeave * call pyeval('vcoq.main.onClose("' . expand('<afile>') . '")')
autocmd WinEnter * call pyeval('vcoq.main.onEnter("' . expand('<afile>') . '")')
autocmd VimResized * py vcoq.main.onVimResized()

" Init the local variables of the current window
function! InitWindow()
	setlocal noreadonly " in case the 'view' mode is used
	setlocal buftype=nofile
	setlocal bufhidden=hide
	setlocal noswapfile
	setlocal nobuflisted
	setlocal nolist
	setlocal nowrap
	setlocal winfixwidth
	setlocal textwidth=0
	setlocal nospell
	setlocal nofoldenable
	setlocal foldcolumn=0
	setlocal foldmethod&
	setlocal foldexpr&
endfunction

" Change window until the window 'win' has focus.
function! FocusWindow(win)
	let num = bufwinnr(a:win)
	while winnr()!= num
		wincmd w
	endwhile
endfunction
