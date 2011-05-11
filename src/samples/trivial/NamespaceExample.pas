unit AboutBox;

interface

uses
  System.Drawing, System.Collections, System.ComponentModel,
  System.Windows.Forms, System.Data, System.Resources;

type
  TAboutBox = class(System.Windows.Forms.Form)
  {$REGION 'Designer Managed Code'}
  strict private
    /// <summary>
    /// Required designer variable.
    /// </summary>
    Components: System.ComponentModel.Container;
    ButtonOK: System.Windows.Forms.Button;
    PictureBoxIcon: System.Windows.Forms.PictureBox;
    LabelProductName: System.Windows.Forms.Label;
    LabelProductVersion: System.Windows.Forms.Label;
    LabelAuthor: System.Windows.Forms.Label;
    /// <summary>
    /// Required method for Designer support - do not modify
    /// the contents of this method with the code editor.
    /// </summary>
    procedure InitializeComponent;
    procedure TAboutBox_Load(sender: System.Object; e: System.EventArgs);
  {$ENDREGION}
  strict protected
    /// <summary>
    /// Clean up any resources being used.
    /// </summary>
    procedure Dispose(Disposing: Boolean); override;
  public
    constructor Create;
    class procedure ShowAboutBox;
  end;

implementation

uses
  System.Globalization, System.Diagnostics;

{$REGION 'Windows Form Designer generated code'}
/// <summary>
/// Required method for Designer support - do not modify
/// the contents of this method with the code editor.
/// </summary>
procedure TAboutBox.InitializeComponent;
var
  resources: System.Resources.ResourceManager;
begin
  resources := System.Resources.ResourceManager.Create(TypeOf(TAboutBox));
  Self.ButtonOK := System.Windows.Forms.Button.Create;
  Self.PictureBoxIcon := System.Windows.Forms.PictureBox.Create;
  Self.LabelProductName := System.Windows.Forms.Label.Create;
  Self.LabelProductVersion := System.Windows.Forms.Label.Create;
  Self.LabelAuthor := System.Windows.Forms.Label.Create;
  Self.SuspendLayout;
  // 
  // ButtonOK
  // 
  Self.ButtonOK.DialogResult := System.Windows.Forms.DialogResult.OK;
  Self.ButtonOK.Location := System.Drawing.Point.Create(152, 112);
  Self.ButtonOK.Name := 'ButtonOK';
  Self.ButtonOK.TabIndex := 0;
  Self.ButtonOK.Text := 'OK';
  // 
  // PictureBoxIcon
  // 
  Self.PictureBoxIcon.Image := (System.Drawing.Image(resources.GetObject('PictureBoxIcon.Image')));
  Self.PictureBoxIcon.Location := System.Drawing.Point.Create(8, 16);
  Self.PictureBoxIcon.Name := 'PictureBoxIcon';
  Self.PictureBoxIcon.Size := System.Drawing.Size.Create(32, 32);
  Self.PictureBoxIcon.SizeMode := System.Windows.Forms.PictureBoxSizeMode.AutoSize;
  Self.PictureBoxIcon.TabIndex := 1;
  Self.PictureBoxIcon.TabStop := False;
  // 
  // LabelProductName
  // 
  Self.LabelProductName.AutoSize := True;
  Self.LabelProductName.Font := System.Drawing.Font.Create('Microsoft Sans Serif', 8.25, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, (System.Byte(238)));
  Self.LabelProductName.Location := System.Drawing.Point.Create(64, 16);
  Self.LabelProductName.Name := 'LabelProductName';
  Self.LabelProductName.Size := System.Drawing.Size.Create(76, 16);
  Self.LabelProductName.TabIndex := 2;
  Self.LabelProductName.Text := 'ProductName';
  // 
  // LabelProductVersion
  // 
  Self.LabelProductVersion.AutoSize := True;
  Self.LabelProductVersion.Location := System.Drawing.Point.Create(64, 40);
  Self.LabelProductVersion.Name := 'LabelProductVersion';
  Self.LabelProductVersion.Size := System.Drawing.Size.Create(82, 16);
  Self.LabelProductVersion.TabIndex := 3;
  Self.LabelProductVersion.Text := 'ProductVersion';
  // 
  // LabelAuthor
  // 
  Self.LabelAuthor.AutoSize := True;
  Self.LabelAuthor.Location := System.Drawing.Point.Create(64, 64);
  Self.LabelAuthor.Name := 'LabelAuthor';
  Self.LabelAuthor.Size := System.Drawing.Size.Create(38, 16);
  Self.LabelAuthor.TabIndex := 4;
  Self.LabelAuthor.Text := 'Author';
  // 
  // TAboutBox
  // 
  Self.AutoScaleBaseSize := System.Drawing.Size.Create(5, 13);
  Self.ClientSize := System.Drawing.Size.Create(242, 151);
  Self.Controls.Add(Self.LabelAuthor);
  Self.Controls.Add(Self.LabelProductVersion);
  Self.Controls.Add(Self.LabelProductName);
  Self.Controls.Add(Self.PictureBoxIcon);
  Self.Controls.Add(Self.ButtonOK);
  Self.FormBorderStyle := System.Windows.Forms.FormBorderStyle.FixedSingle;
  Self.MaximizeBox := False;
  Self.MinimizeBox := False;
  Self.Name := 'TAboutBox';
  Self.ShowInTaskbar := False;
  Self.StartPosition := System.Windows.Forms.FormStartPosition.CenterScreen;
  Self.Text := 'About ...';
  Include(Self.Load, Self.TAboutBox_Load);
  Self.ResumeLayout(False);
end;
{$ENDREGION}

procedure TAboutBox.Dispose(Disposing: Boolean);
begin
  if Disposing then
  begin
    if Components <> nil then
      Components.Dispose();
  end;
  inherited Dispose(Disposing);
end;

constructor TAboutBox.Create;
begin
  inherited Create;
  //
  // Required for Windows Form Designer support
  //
  InitializeComponent;
  //
  // TODO: Add any constructor code after InitializeComponent call
  //
end;

class procedure TAboutBox.ShowAboutBox;
begin
  TAboutBox.Create.ShowDialog;
end;

procedure TAboutBox.TAboutBox_Load(sender: System.Object; e: System.EventArgs);
var
  Version: FileVersionInfo;
begin
  Version := FileVersionInfo.GetVersionInfo(Application.ExecutablePath);
  LabelProductName.Text := Application.ProductName;
  LabelProductVersion.Text := System.String.Format('Version: {0}.{1}', [Version.ProductMajorPart, Version.ProductMinorPart]);
  LabelAuthor.Text := System.String.Format('Author: {0}', [Version.CompanyName]);
end;

end.
