program Flagship;

uses
  Forms,
  MainWindow in '..\MainWindow.pas' {FormWindow};

{$R *.res}

begin
  Application.Initialize;
  Application.CreateForm(TFormWindow, FormWindow);
  Application.Run;
end.
