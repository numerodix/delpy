unit Parsing;

interface

implementation

function Draw(const X, Y: Integer; 
	Sender: string;
	var Desc: string): Integer; stdcall;
const
  Z = 'begin here';
  Z2 = 'end here';
var
  R: Integer; 
  TT: string;
begin
  Result := X;
end;

end.
