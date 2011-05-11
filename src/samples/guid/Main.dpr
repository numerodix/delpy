program Main;

procedure SayHi;
begin
  WriteLn('Saying hi now'); // greppable string in executable
end;

procedure SaveMe;
begin
  WriteLn('Saving now'); // not found, unreached procedure not linked
end;

begin
  SayHi();
end.
