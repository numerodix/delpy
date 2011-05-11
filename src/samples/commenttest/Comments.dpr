program{ comment }Comments;

{$APPTYPE CONSOLE}
(*$APPTYPE CONSOLE*)

uses
  SysUtils;

begin
  // c style
  { braces }
  (* parens *)

  { // } Writeln('C style inside braces are not comments');
  (* // *) Writeln('C style inside parens are not comments');
  { { asd } Writeln('Braces do not nest');
  (* (* asd *) Writeln('Parens do not nest');
  (*) *) Writeln('Not a comment without both tokens in full');

  { comment
    (*)
  } Writeln('after first');

  (* comment
	{}
  *) Writeln('after second');

  (*
	{
  *) Writeln('after third');

  {
	(* *)
  } Writeln('after fourth');

  Writeln('Comment inside a string is {not} a comment');
  Writeln('// Write this comment to c');

  Writeln('Strings can have ''single quotes too');
end.
