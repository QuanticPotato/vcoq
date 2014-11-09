let s:current_dir=expand("<sfile>:p:h")
py import sys, vim
py if not vim.eval("s:current_dir") in sys.path:
	\  sys.path.append(vim.eval("s:current_dir"))
py import vcoq

function! LaunchC() 
	py vcoq.init()
endfunction

autocmd BufEnter * py vcoq.bufferFocusChange(True)
autocmd BufLeave * py vcoq.bufferFocusChange(False)

autocmd VimResized * :call UpdateWindows()

function! UpdateWindows()
	call UpdateWindowsNumber()
	py vcoq.updateWindows()
endfunction

" Fill the editWindow, goalsWindow, tagbarWindow ... script variables
function! UpdateWindowsNumber()
	let s:editWindow = UpdateWindowNr('Edit')
	let s:consoleWindow = UpdateWindowNr('Console_output')
	let s:tagbarWindow = UpdateWindowNr('Tags')
	let s:compiledWindow = UpdateWindowNr('Accepted_statements')
	let s:goalsWindow = UpdateWindowNr('Goals')
	let s:inputWindow = UpdateWindowNr('Console_input')
endfunction

function! UpdateWindowNr(buffName)
	let l:windowNumber = bufwinnr(a:buffName)
	if l:windowNumber == -1
		echoe 'The ' . a:buffName . ' window has been closed !'	
		" TODO kill the vcoq
	endif
	return l:windowNumber
endfunction

