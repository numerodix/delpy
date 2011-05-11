object FormWindow: TFormWindow
  Left = 0
  Top = 0
  Caption = 'MainWindow'
  ClientHeight = 171
  ClientWidth = 364
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object CLbl: TLabel
    Left = 72
    Top = 74
    Width = 60
    Height = 23
    Alignment = taCenter
    Caption = '<Idle>'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -19
    Font.Name = 'Tahoma'
    Font.Style = []
    ParentFont = False
  end
  object CButton: TButton
    Left = 192
    Top = 68
    Width = 105
    Height = 38
    Caption = 'Clicca qui'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -19
    Font.Name = 'Tahoma'
    Font.Style = []
    ParentFont = False
    TabOrder = 0
    OnClick = CButtonClick
  end
end
