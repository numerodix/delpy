unit MainWindow;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls;

type
  TFormWindow = class(TForm)
    CButton: TButton;
    CLbl: TLabel;
    procedure CButtonClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  FormWindow: TFormWindow;

implementation

{$R *.dfm}

uses
  Module,
  Lib;

procedure TFormWindow.CButtonClick(Sender: TObject);
begin
  CLbl.Caption := Module.lbl;
  FormWindow.Caption := FormWindow.Caption + ' v' + Lib.version;
end;

end.
