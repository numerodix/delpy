program CodedGui;

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls;

type
  TMainGui = class(TForm)
	Button: TButton;
	constructor Create(Owner: TComponent); override;
	procedure ButtonClicked(Sender: TObject);
  end;

var
  MainGui: TMainGui;

{$R *.dfm}

constructor TMainGui.Create(Owner: TComponent);
begin
  inherited Create(Owner);
  Button := TButton.Create(self);
  Button.Top := 0;
  Button.Left := 0;
  Button.Height := 30;
  Button.Width := 100;
  Button.Caption := 'Clicky';
  Button.OnClick := ButtonClicked;
  Button.Parent := self;
end;

procedure TMainGui.ButtonClicked(Sender: TObject);
begin
  Button.Caption := 'Clicked!';
end;



begin
  Application.Initialize;
  Application.Title := 'CodedGui';
  Application.CreateForm(TMainGui, MainGui);
  Application.Run;
end.
