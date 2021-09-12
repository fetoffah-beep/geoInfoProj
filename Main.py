# -*- coding: utf-8 -*- 
#!/usr/bin/env python

import os
import wx
import wx.xrc
import wx.adv
import geopandas as gpd
import numpy as np
from wx.html import HtmlWindow
from wx.html import HtmlHelpController

# Import defined functions
from functions.ionosphericCorrectionSF import ionoCorrection as iono
from functions.sat_orbit import SatelliteInfo
from functions.read_rinex import readIonosphericParamters as readIono
from functions.read_rinex import read_nav as rNav
from functions.read_rinex import getSatellitePRN as gsp


# Plotting modules
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
import cartopy.crs as ccrs
from astroplan.plots import plot_sky
from datetime import datetime
matplotlib.use('WXAgg')


###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"GNSS Data Processing", pos = wx.DefaultPosition, size = (750,480), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        
        vSizer = wx.BoxSizer( wx.VERTICAL )     # Horinzontal box sizer
        
        self.SetSizer( vSizer )
        self.Layout()
        

        # Add an icon
        icon = wx.Icon('images/gnss.ico', type = wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)

        ###############################################
        # MENU BAR
        ###############################################
        self.MenuBar = wx.MenuBar( 0 )
        #self.FileMenu = wx.Menu()

        # File menu and its items
        #self.FileMenu.AppendSeparator()

        # self.closeMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Close"+ u"\t" + u"Alt + F4", wx.EmptyString, wx.ITEM_NORMAL )
        # self.FileMenu.Append( self.closeMenu )
        
        # self.MenuBar.Append( self.FileMenu, u"&File" ) 
        
        #Input menu
        self.InputMenu = wx.Menu()
        self.openMenu = wx.MenuItem( self.InputMenu, wx.ID_ANY, u"&Open"+ u"\t" + u"Ctrl + O", wx.EmptyString, wx.ITEM_NORMAL )
        self.InputMenu.Append( self.openMenu )
        self.InputMenu.AppendSeparator()
        self.closeMenu = wx.MenuItem( self.InputMenu, wx.ID_ANY, u"&Close"+ u"\t" + u"Alt + F4", wx.EmptyString, wx.ITEM_NORMAL )
        self.InputMenu.Append( self.closeMenu )
        
        self.MenuBar.Append( self.InputMenu, u"&Input" )
        
        
        # Help menu for the about page and help contents
        self.HelpMenu = wx.Menu()

        self.helpContentMenuItem = wx.MenuItem( self.HelpMenu, wx.ID_ANY, u"&Help Content", wx.EmptyString, wx.ITEM_NORMAL )
        self.HelpMenu.Append( self.helpContentMenuItem )


        self.HelpMenu.AppendSeparator()

        self.aboutMenuItem = wx.MenuItem( self.HelpMenu, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL )
        self.HelpMenu.Append( self.aboutMenuItem )
        
        self.MenuBar.Append( self.HelpMenu, u"&Help" ) 
        
        self.SetMenuBar( self.MenuBar )


        # Create accelerator for the menu buttons, i.e, the shortcuts
        shortCuts = [wx.AcceleratorEntry() for i in range(3)]
        shortCuts[0].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_O, self.openMenu.GetId())
        shortCuts[1].Set(wx.ACCEL_ALT, wx.WXK_F4, self.closeMenu.GetId())
        shortCuts[2].Set(wx.ACCEL_NORMAL, wx.WXK_F1, self.helpContentMenuItem.GetId())

        accel = wx.AcceleratorTable(shortCuts)
        self.SetAcceleratorTable(accel) 


        ##########################################################
        #   NOTEBOOK CONTAINERS
        ##########################################################
        
        self.noteBook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH|wx.NB_TOP )
        orbitNoteBookWindow = orbitNoteBookPanel(self.noteBook)
        ionoNoteBookWindow = ionosphereNoteBookPanel(self.noteBook)
        
        # Add the pages to the noteBook
        self.noteBook.AddPage(orbitNoteBookWindow, 'Orbit')
        self.noteBook.AddPage(ionoNoteBookWindow, 'Ionosphere')
        

        vSizer.Add( self.noteBook, 1, wx.EXPAND|wx.ALL, 5 )


        #################################################
        #   STATUS BAR
        #################################################
        self.statusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
        
        self.Centre( wx.BOTH )


        # ---------------------------Connect Events ------------------------------------------------
        # Menu events
        self.Bind( wx.EVT_MENU, self.onOpen, id = self.openMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.CloseFunc, id = self.closeMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.helpContent, id = self.helpContentMenuItem.GetId() )
        self.Bind( wx.EVT_MENU, self.aboutPage, id = self.aboutMenuItem.GetId() )

        
    def __del__( self ):
        pass

    def onOpen (self, event):
        try:
            file = wx.FileDialog(self, message = "Select a file", defaultDir = os.getcwd(), defaultFile="", wildcard=u"Rinex (*.rnx)|*.rnx|Navigation file (*.*n)|*.*n|All files(*.)| *.*", style= wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if file.ShowModal() != wx.ID_OK:
                return

            # Get the path of the file
            MainFrame.onOpen.filePath = file.GetPath()

            # Check on the file extension to be opened
            filePath = MainFrame.onOpen.filePath
            if ( os.path.splitext(filePath)[1] != '.rnx' ) and (os.path.splitext(filePath)[1][3] != 'n'):
                dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx | .*n)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

            # Get the available satellite PRN in the file
            MainFrame.onOpen.satellitePRN =   gsp( MainFrame.onOpen.filePath )


            file.Destroy()

        except Exception as err:
            dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx | .*n)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return

        #Checks on file type and other warnings
        with open(MainFrame.onOpen.filePath,'r') as file:
            for line in file:
                if 'RINEX VERSION' in line:
                    word = line.split()

                    # Check the rinex version of file
                    if float(word[0]) > 3.05:
                        dlg = wx.MessageDialog(None, 'Rinex file version is not supported', 'File Version Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                        dlg.ShowModal()
                        dlg.Destroy()
                        return

                    # check that the file is a navigation message file
                    if ((word[1] != 'NAVIGATION') and (word[3] != 'G')) and ((word[1][0]!='N') and (word[5][0]!='G')):
                        dlg = wx.MessageDialog(None, 'Selected file is not of Navigation message type', 'File type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                        dlg.ShowModal()
                        dlg.Destroy()
                        return

                # check that at least one SV message is in the file
                if 'END OF HEADER' in line:
                    if file.read()=='' and len(MainFrame.onOpen.satellitePRN)==0:
                        dlg = wx.MessageDialog(None, 'No navigation data was found in the selected file', 'Empty Nav File', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                        dlg.ShowModal()
                        dlg.Destroy()
                        return

        # Check of ionospheric parameters
        ionoParams = readIono( MainFrame.onOpen.filePath )

        if len(ionoParams) == 0:
            dlg = wx.MessageDialog(None, 'Please note that the selected file does not have Ionospheric Correction Parameters', 'Alert', wx.OK|wx.ICON_INFORMATION, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return    

   

    def aboutPage(self, event):
        dlg = AboutPage(self)
        dlg.ShowModal()
        dlg.Destroy()

  

    def helpContent( self, event ):
        html  = HtmlHelpController(style=wx.html.HF_TOOLBAR | wx.html.HF_CONTENTS | wx.html.HF_INDEX | wx.html.HF_SEARCH | wx.html.HF_PRINT, parentWindow=None)
        html.AddBook(u"Document/User Manual.hhp")
        html.Display(u"Document/Table Of Contents.hhc")
        html.Show()

    def CloseFunc( self, event ):
        self.Close()


class AboutPage(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id = wx.ID_ANY, title = 'About GNSS Data Processing SOFTWARE', pos = wx.DefaultPosition, size = wx.Size( 350,410 ), style = wx.DEFAULT_DIALOG_STYLE )
        html  = wx.html.HtmlWindow(self)
        html.LoadPage(u"functions/about.html")


###########################################################################
##  Note Book Classes
###########################################################################

# -------------------------------Satellite orbit parameter------------------------------#             
class orbitNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # Create the static box for receiving parameters for the functionalities
        satelliteStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Satellite Orbit Parameters" ), wx.HORIZONTAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( satelliteStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        
        # Add spacer for a nicer view
        satelliteStaticbox.AddSpacer(10)
        
        
        orbitSizerLeft = wx.BoxSizer( wx.VERTICAL )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.choiceStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Preferred Mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.choiceStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.choiceStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.prnStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter PRN number of SV (eg. 01, 02 etc.):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.prnStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.prnStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.refStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter position of Reference (Deg Decimal, m):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.refStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.refStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.longStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Longitude:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.longStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.longStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.latStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Latitude:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.latStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.latStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerLeft.AddSpacer(10)
        
        self.hStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Height:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.hStaticText.Wrap( -1 )
        orbitSizerLeft.Add( self.hStaticText, 0, wx.ALL, 5 )
        
        
        satelliteStaticbox.Add( orbitSizerLeft, 0, wx.EXPAND, 1 )
        
        orbitSizerRight = wx.BoxSizer( wx.VERTICAL )
        
        choiceChoices = [ u"Global Map (ground track)", u"Local Map (azimuth/elevation)" ]
        self.choice = wx.Choice( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceChoices, wx.CB_SORT )
        orbitSizerRight.Add( self.choice, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerRight.AddSpacer(5)

        self.prnTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
        orbitSizerRight.Add( self.prnTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerRight.AddSpacer(35)

        
        self.longTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
        orbitSizerRight.Add( self.longTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerRight.AddSpacer(5)
        
        self.latTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
        orbitSizerRight.Add( self.latTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        orbitSizerRight.AddSpacer(5)
        
        self.hTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
        orbitSizerRight.Add( self.hTextCtrl, 0, wx.ALL, 5 )
        
        
        satelliteStaticbox.Add( orbitSizerRight, 0, wx.ALL, 5 )
        
        
        self.orbitPoceedButton = wx.Button( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        satelliteStaticbox.Add( self.orbitPoceedButton, 0, wx.ALIGN_BOTTOM|wx.ALL, 5 )
        

        #Show relevant boxes only after mode selection
        wx.CallAfter(self.prnStaticText.Show, False)
        wx.CallAfter(self.prnTextCtrl.Show, False)
        wx.CallAfter(self.refStaticText.Show, False)
        wx.CallAfter(self.longStaticText.Show, False)
        wx.CallAfter(self.longTextCtrl.Show, False)
        wx.CallAfter(self.latStaticText.Show, False)
        wx.CallAfter(self.latTextCtrl.Show, False)
        wx.CallAfter(self.hStaticText.Show, False)
        wx.CallAfter(self.hTextCtrl.Show, False)
        wx.CallAfter(self.orbitPoceedButton.Show, False)

        # Connected events
        self.choice.Bind( wx.EVT_CHOICE, self.OnChoice )
        self.orbitPoceedButton.Bind( wx.EVT_BUTTON, self.OrbitCompute )
        
        self.SetSizer( noteBookSizer )
        self.Layout()


    def OrbitCompute(self, event):
        try:
            filePath = MainFrame.onOpen.filePath
            if ( os.path.splitext(filePath)[1] != '.rnx' ) and (os.path.splitext(filePath)[1][3] != 'n'):
                dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx | .*n)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

            userPRN = self.prnTextCtrl.GetValue()
            availablePRN = MainFrame.onOpen.satellitePRN
            availablePRN.sort()
        
            try:
                numberPRN=int(userPRN)
            except Exception as err:
                dlg = wx.MessageDialog(None, 'PRN must be an integer number', 'Input Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return  
        
            if userPRN not in availablePRN:
                dlg = wx.MessageDialog(None, 'The SV PRN is not available. Available ones are: ' + ', '.join(availablePRN), 'PRN Unavilability', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

        except Exception as err:
            dlg = wx.MessageDialog(None, 'No navigation file has been selected \n \n Click Input -> Open to select file', 'File Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return
        
                
        if self.choice.GetStringSelection() ==  "Global Map (ground track)":
            #ORBIT
            satelliteOrbit = SatelliteInfo( filePath, userPRN, 0, 0, 0, False )
            
            plt.figure()
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.stock_img()
            #ax.coastlines()
            ax.gridlines()
            
            #plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'ro--', linewidth=2, markersize=7, transform=ccrs.Geodetic())
            plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'ro', markersize=7, transform=ccrs.Geodetic())
            #plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'b', linewidth=3, transform=ccrs.Geodetic())
            font1={'family':'serif','color':'black','size':15}
            plt.title('Satellite G'+str(userPRN)+'\n(from '+str(satelliteOrbit.first_datetime)+' to '+str(satelliteOrbit.last_datetime)+')', fontdict=font1)
            #plt.suptitle()
        
        else:
            #ANGLES
            try:
                longitude = self.longTextCtrl.GetValue()
                latitude = self.latTextCtrl.GetValue()
                height = self.hTextCtrl.GetValue()
                
                # Check that the parameters are not empty
                if self.longTextCtrl.GetValue() == '' or self.latTextCtrl.GetValue() == '' or self.hTextCtrl.GetValue() == '':
                    dlg = wx.MessageDialog(None, 'Check that all parameter values are entered', 'Parameter Empty', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                
                # Check the range of the entered values
                if float(longitude) > 180 or float(longitude) < -180 or float(latitude) > 90 or float(latitude) < -90:
                    dlg = wx.MessageDialog(None, 'Value entered is out of range', 'Value error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

                angles = SatelliteInfo( filePath, userPRN, longitude, latitude, height, True )
            
                #Azimuth and elevation
                font1={'family':'serif','color':'black','size':16}
            
                fig, (ax1, ax2) = plt.subplots(2, 1)
                fig.suptitle('Satellite: G'+str(userPRN), size=20)

                ax1.plot(angles.sv_datetimes, angles.sv_azimuth, 'ro', linewidth=2)
                ax1.set_ylabel('Azimuth', fontdict=font1)
                ax1.grid()

                ax2.plot(angles.sv_datetimes, angles.sv_elevation, 'bo', linewidth=2)
                ax2.set_xlabel('Time', fontdict=font1)
                ax2.set_ylabel('Elevation', fontdict=font1)
                ax2.grid()            
            except Exception as err:
                dlg = wx.MessageDialog(None, 'Only numerical values are allowed', 'Data type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return               


    def OnChoice (self, event):
        self.user_choice = event.GetString()
        if self.user_choice == 'Local Map (azimuth/elevation)':
            self.prnStaticText.Show(True)
            self.prnTextCtrl.Show(True)
            self.refStaticText.Show(True)
            self.longStaticText.Show(True)
            self.longTextCtrl.Show(True)
            self.latStaticText.Show(True)
            self.latTextCtrl.Show(True)
            self.hStaticText.Show(True)
            self.hTextCtrl.Show(True)
            self.orbitPoceedButton.Show(True) 
        else:
            self.prnStaticText.Show(True)
            self.prnTextCtrl.Show(True)
            self.refStaticText.Show(False)
            self.longStaticText.Show(False)
            self.longTextCtrl.Show(False)
            self.latStaticText.Show(False)
            self.latTextCtrl.Show(False)
            self.hStaticText.Show(False)
            self.hTextCtrl.Show(False)
            self.orbitPoceedButton.Show(True)
            
        

       
# ------------------------------- Ionospheric Error Parameter ------------------------------#             

class ionosphereNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # Create the static box for receiving parameters for the functionalities
        ionosphereStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Ionosphere Parameters" ), wx.HORIZONTAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( ionosphereStaticbox, 1, wx.ALL|wx.EXPAND, 15 )

       
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)


        ionoSizerLeft = wx.BoxSizer( wx.VERTICAL )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(5)
        
        self.choiceStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Preferred Mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.choiceStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.choiceStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(8)
        

        self.timeStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Time (HH: MM: SS):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.timeStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.timeStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(10)
        
        
        self.elevStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Elevation (Deg Decimal):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.elevStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.elevStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(10)
        
        
        self.azStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Azimuth (Deg Decimal):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.azStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.azStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(10)
        
        
        self.longStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Longitude (Deg Decimal):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.longStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.longStaticText, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerLeft.AddSpacer(10)
        
        
        self.latStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Latitude (Deg Decimal):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.latStaticText.Wrap( -1 )
        ionoSizerLeft.Add( self.latStaticText, 0, wx.ALL, 5 )
        
        
        ionosphereStaticbox.Add( ionoSizerLeft, 0, wx.EXPAND, 5 )



        # -----------------------------------------
        ionoSizerRight = wx.BoxSizer( wx.VERTICAL )
        
        choiceChoices = [ u"Global Map", u"Local Map" ]
        self.choice = wx.Choice( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceChoices, wx.CB_SORT )
        ionoSizerRight.Add( self.choice, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerRight.AddSpacer(3)

        timeSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.timeHHControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", (wx.DefaultPosition), wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=23, initial=0)
        timeSizer.Add( self.timeHHControl, 0, wx.ALL, 5 )

        self.timeMMControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=59, initial=0)
        timeSizer.Add( self.timeMMControl, 0, wx.ALL, 5 )

        self.timeSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=59, initial=0)
        timeSizer.Add( self.timeSSControl, 0, wx.ALL, 5 )
        
        
        ionoSizerRight.Add( timeSizer, 0, 0, 5 )

        # Add spacer for a nicer view
        ionoSizerRight.AddSpacer(2)
        
        self.elevTextCtrl = wx.TextCtrl( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB|wx.TE_RIGHT )
        ionoSizerRight.Add( self.elevTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerRight.AddSpacer(4)
        
        self.azTextCtrl = wx.TextCtrl( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB|wx.TE_RIGHT )
        ionoSizerRight.Add( self.azTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerRight.AddSpacer(5)
        
        self.longTextCtrl = wx.TextCtrl( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB|wx.TE_RIGHT )
        ionoSizerRight.Add( self.longTextCtrl, 0, wx.ALL, 5 )

        # Add spacer for a nicer view
        ionoSizerRight.AddSpacer(7)
        
        self.latTextCtrl = wx.TextCtrl( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB|wx.TE_RIGHT )
        ionoSizerRight.Add( self.latTextCtrl, 0, wx.ALL, 5 )
        
        
        ionosphereStaticbox.Add( ionoSizerRight, 1, wx.EXPAND, 5 )

        self.proceedButton = wx.Button( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        ionosphereStaticbox.Add( self.proceedButton, 0, wx.ALIGN_BOTTOM|wx.ALL, 5 )

        
     
        # Show the relevant boxes after the mode has been selected by the user
        wx.CallAfter(self.timeStaticText.Show, False)
        wx.CallAfter(self.timeHHControl.Show, False)
        wx.CallAfter(self.timeMMControl.Show, False)
        wx.CallAfter(self.timeSSControl.Show, False)
        wx.CallAfter(self.elevStaticText.Show, False)
        wx.CallAfter(self.elevTextCtrl.Show, False)
        wx.CallAfter(self.azStaticText.Show, False)
        wx.CallAfter(self.azTextCtrl.Show, False)
        wx.CallAfter(self.longStaticText.Show, False)
        wx.CallAfter(self.longTextCtrl.Show, False)
        wx.CallAfter(self.latStaticText.Show, False)
        wx.CallAfter(self.latTextCtrl.Show, False)
        wx.CallAfter(self.proceedButton.Show, False)
        
        


        # Connected events
        self.choice.Bind( wx.EVT_CHOICE, self.OnChoice )
        self.proceedButton.Bind( wx.EVT_BUTTON, self.IonosphereCompute )
        
        self.SetSizer( noteBookSizer )
        self.Layout()

    def IonosphereCompute( self, event ):
        
        try:
            filePath = MainFrame.onOpen.filePath
            if ( os.path.splitext(filePath)[1] != '.rnx' ) and (os.path.splitext(filePath)[1][3] != 'n'):
                dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

        except Exception as err:
            dlg = wx.MessageDialog(None, 'No navigation file (.rnx) has been selected \n \n Click Input -> Open to select file', 'File Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # ---------------------COMPUTE IONO CORR-----------------------------------------
        ionoParams = readIono( filePath )

        if len(ionoParams) == 0:
            dlg = wx.MessageDialog(None, 'Selected file does not have Ionospheric Correction Parameters', 'Information', wx.OK|wx.ICON_INFORMATION, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return

        
        # ---------------------PLOT IONO MAP -----------------------------------------
        if self.choice.GetStringSelection() == 'Local Map':

            
            try:
                # Check that the parameters are not empty
                if self.longTextCtrl.GetValue() == '' or self.latTextCtrl.GetValue() == '':
                    dlg = wx.MessageDialog(None, 'Check that all parameter values are entered', 'Parameter Empty', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                elevation = np.linspace(0, 90, 181)
                azimuth = np.linspace(-180, 180, 721)
                longitude = float(self.longTextCtrl.GetValue())
                latitude = float(self.latTextCtrl.GetValue())

                # Check the range of the entered values
                if longitude > 180 or longitude < -180 or latitude > 90 or latitude < -90:
                    dlg = wx.MessageDialog(None, 'Value entered is out of range', 'Value error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

                time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
                
                stationPoints = np.zeros((len(elevation), len(azimuth)))

                for elev in range(len(elevation)):
                    for azim in range(len(azimuth)):
                        stationPoints[elev][azim] = iono(latitude, longitude, azimuth[azim], elevation[elev], time, ionoParams[0])
                
                x,y = np.meshgrid(azimuth, elevation)

                x = np.flip( x * np.pi / 180, 1)
                y = y * np.pi / 180

                stationPoints = np.flip( stationPoints, (0, 1) )

                fig1, ax2 = plt.subplots(subplot_kw=dict(projection='polar'), constrained_layout=False)
                CS = ax2.contourf(x, y, stationPoints, 100, cmap=cm.jet)
                ax2.set_theta_zero_location('N')
                ax2.set_theta_direction(-1)
                ax2.set_title('Ionospheric delay at time = {} : {} : {} '.format( self.timeHHControl.GetValue(), self.timeMMControl.GetValue(), self.timeSSControl.GetValue()))
                ax2.set_ylim(0, np.pi/2)
                ax2.set_rticks([np.pi/2, np.pi/2.4, np.pi/3, np.pi/4, np.pi/6, np.pi/12, 0])
                ax2.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
                ax2.set_yticklabels(['0\u00B0', '15\u00B0', '30\u00B0', '45\u00B0', '60\u00B0', '75\u00B0', '90\u00B0'])
            except Exception as err:
                dlg = wx.MessageDialog(None, 'Only numerical values are allowed', 'Data type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return


        else:
            try:
                # Check that the parameters are not empty
                if self.elevTextCtrl.GetValue() == '' or self.azTextCtrl.GetValue() == '':
                    dlg = wx.MessageDialog(None, 'Check that all parameter values are entered', 'Parameter Empty', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                    
                elevation = float(self.elevTextCtrl.GetValue())
                azimuth = float(self.azTextCtrl.GetValue())
                longitude = np.linspace(-180, 180, 721) 
                latitude = np.linspace(-90, 90, 361) 
                time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
                
                # Check the range of the entered values
                if elevation > 90 or elevation < 0 or azimuth > 180 or azimuth < -180:
                    dlg = wx.MessageDialog(None, 'Value entered is out of range', 'Value error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return


                stationPoints = np.zeros((len(latitude), len(longitude)))
                
                
                for lat in range(len(latitude)):
                    for longit in range(len(longitude)):
                        stationPoints[lat][longit] = iono(latitude[lat], longitude[longit], azimuth, elevation, time, ionoParams[0])
                
                x,y = np.meshgrid(longitude, latitude)
                
                fig1, ax2 = plt.subplots(constrained_layout=False)

                CS = ax2.contourf(x, y, stationPoints, 100, cmap=cm.jet)
            
                ax2.set_title('Ionospheric delay at time = {} : {} : {} '.format( self.timeHHControl.GetValue(), self.timeMMControl.GetValue(), self.timeSSControl.GetValue()))
                ax2.set_xlabel('Longitude (\u00B0)')
                ax2.set_ylabel('Latitude (\u00B0)')
                ax2.set_xlim([-180, 180])
                ax2.set_ylim([-90, 90])
                worldMap = gpd.read_file(r'worldMap/ne_10m_admin_0_countries.shp')
                worldMap.plot(ax=ax2, facecolor='none', edgecolor='black', lw=0.15)
            except Exception as err:
                dlg = wx.MessageDialog(None, 'Only numerical values are allowed', 'Data Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

        cbar = plt.colorbar(CS)
        cbar.ax.set_ylabel('[m]')
        ionoMap = plt.show()
        


    def OnChoice (self, event):
        self.user_choice = event.GetString()
        if self.user_choice == 'Local Map':
            self.timeStaticText.Show(True)
            self.timeHHControl.Show(True)
            self.timeMMControl.Show(True)
            self.timeSSControl.Show(True)
            self.elevStaticText.Show(False)
            self.elevTextCtrl.Show(False)
            self.azStaticText.Show(False)
            self.azTextCtrl.Show(False)
            self.longStaticText.Show(True)
            self.longTextCtrl.Show(True)
            self.latStaticText.Show(True)
            self.latTextCtrl.Show(True)
            self.proceedButton.Show(True)
            
        else:
            self.timeStaticText.Show(True)
            self.timeHHControl.Show(True)
            self.timeMMControl.Show(True)
            self.timeSSControl.Show(True)
            self.elevStaticText.Show(True)
            self.elevTextCtrl.Show(True)
            self.azStaticText.Show(True)
            self.azTextCtrl.Show(True)
            self.longStaticText.Show(False)
            self.longTextCtrl.Show(False)
            self.latStaticText.Show(False)
            self.latTextCtrl.Show(False)
            self.proceedButton.Show(True)

 
###########################################################################
## RUN THE MODEL
###########################################################################

# check that the module is being run as a program and imported   
if __name__ == '__main__':
    app = wx.App()
    # The main frame object is created after creating the application object as the app is needed for the frame to execute
    frame = MainFrame(None)
    frame.Show()
    #frame.Maximize(True)        # Maximize the window on first load
    app.MainLoop()