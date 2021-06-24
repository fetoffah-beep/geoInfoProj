# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 250,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.DisplayResult = wx.StaticText( self, wx.ID_ANY, u"Relative Orientation", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
        self.DisplayResult.Wrap( -1 )
        self.DisplayResult.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer1.Add( self.DisplayResult, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.EnterExpression = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        self.EnterExpression.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer1.Add( self.EnterExpression, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.Button1 = wx.Button( self, wx.ID_ANY, u"Evaluate", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Button1.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer1.Add( self.Button1, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.Button2 = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Button2.SetFont( wx.Font( 15, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer1.Add( self.Button2, 0, wx.ALL|wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.Button1.Bind( wx.EVT_BUTTON, self.EvaluateFunc )
        self.Button2.Bind( wx.EVT_BUTTON, self.CloseFunc )
    
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def EvaluateFunc( self, event ):
        try:
            exp = self.EnterExpression.GetValue()
            Result = str(eval(exp))
            self.DisplayResult.SetLabel(Result)
        except:
            self.DisplayResult.SetLabel("Invalid Expression")


    
    def CloseFunc( self, event ):
        self.Close()
    
app = wx.App()
frame = MyFrame1(wx.Frame(None, -1, 'Relative Orientation'))
frame.Show()
app.MainLoop()
















