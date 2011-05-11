unit Env;

interface

function Get(): string;

implementation

function Get(): string;
var
  str : string;
begin
  str := 'PATH: c:\';
  Result := str;
end;

end.
