unit Libby;

interface

function Add(X, Y: Integer): Integer; overload;
function Add(X, Y: String): Integer; overload;

function UsingBa: Integer;

function HaveDefault(X: Integer = 2): Integer;

implementation

function Add(X: String; Y: String): Integer;
begin
  Result := -1;
end;

function Add(X: Integer; Y: Integer): Integer;
begin
  Result := X + Y;
end;


function Ba: Integer; forward;

function UsingBa: Integer;
begin
  Result := Ba;
end;

function Ba: Integer;
begin
  Result := -7;
end;


function HaveDefault(X: Integer = 2): Integer;
begin
  Result := X;
end;

end.
