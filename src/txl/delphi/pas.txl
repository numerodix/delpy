% Name:   pas.txl
% Purpose:  TXL program for parsing Delphi
% Author:   Jorge L. Cangas
% Author:   Martin Matusiak

#pragma -in 2
 
include "delphi.grammar"
include "delphi_comment.grammar"

include "asm.grammar"


define program
    [delphi_file]
end define

function main
    replace [program]
        P [delphi_file]
    by
        P
end function
