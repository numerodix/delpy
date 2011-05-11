program PriceCheck;

uses
  Forms,
  Gui in 'Gui.pas' {FormMain};

{$R *.res}

begin
  Application.Initialize;
  Application.CreateForm(TFormMain, FormMain);
  Application.Run;
end.
