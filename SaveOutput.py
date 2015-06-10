# $language = "python"
# $interface = "1.0"

# Author: Jamie Caesar
# Twitter: @j_cae
# 
# This SecureCRT script will prompt the user for a command to a Cisco IOS or NX-OS 
# device and dump the output to a file.  The path where the file is saved is
# specified in the "savepath" variable in the Main() function.
#
# This script is tested on SecureCRT version 7.2 on OSX Mavericks
#


import os
import datetime

savepath = 'Dropbox/SecureCRT/Backups/'
mydatestr = '%Y-%m-%d-%H-%M-%S'

def GetHostname(tab):
    '''
    This function will capture the prompt of the device.  The script will capture the
    text that is sent back from the remote device, which includes what we typed being
    echoed back to us, so we have to account for that while we parse data.
    '''
    #Send two line feeds
    tab.Send("\n\n")
    
    # Waits for first linefeed to be echoed back to us
    tab.WaitForString("\n") 
    
    # Read the text up to the next linefeed.
    prompt = tab.ReadString("\n") 

    #Remove any trailing control characters
    prompt = prompt.strip()

    # Check for non-enable mode (prompt ends with ">" instead of "#")
    if prompt[-1] == ">": 
        return None

    # Get out of config mode if that is the active mode when the script was launched
    elif "(conf" in prompt:
        tab.Send("end\n")
        hostname = prompt.split("(")[0]
        tab.WaitForString(hostname + "#")
        # Return the hostname (everything before the first "(")
        return hostname
        
    # Else, Return the hostname (all of the prompt except the last character)        
    else:
        return prompt[:-1]


def WriteOutput(command, filename, prompt, tab):
    '''
    This function captures the raw output of the command supplied and returns it.
    The prompt variable is used to signal the end of the command output, and 
    the "tab" variable is object that specifies which tab the commands are 
    written to. 
    '''
    endings=["\r\n", prompt]
    newfile = open(filename, 'wb')

    # Send term length command and wait for prompt to return
    tab.Send('term length 0\n')
    tab.WaitForString(prompt)
    
    # Send command
    tab.Send(command)

    # Ignore the echo of the command we typed (including linefeed)
    tab.WaitForString(command.strip() + "\r\n")

    # Loop to capture every line of the command.  If we get CRLF (first entry
    # in our "endings" list), then write that line to the file.  If we get
    # our prompt back (which won't have CRLF), break the loop b/c we found the
    # end of the output.
    while True:
        nextline = tab.ReadString(endings)
        # If the match was the 1st index in the endings list -> \r\n
        if tab.MatchIndex == 1:
            # Write the line of text to the file
            newfile.write(nextline + "\r\n")
        else:
            # We got our prompt, so break the loop
            break
    
    newfile.close()
    
    # Send term length back to default
    tab.Send('term length 24\n')
    tab.WaitForString(prompt)


def Main():
    '''
    This purpose of this program is to capture the output of the command entered by the
    user and save it to a file.  This method is much faster than manually setting a log
    file, or trying to extract only the information needed from the saved log file.
    '''
    SendCmd = crt.Dialog.Prompt("Enter the command to capture")
    if SendCmd == "":
        return
    else:
        # Save command without spaces to use in output filename.
        CmdName = SendCmd.replace(" ", "_")
        # Add a newline to command before sending it to the remote device.
        SendCmd = SendCmd + "\r\n"

    # Create a "Tab" object, so that all the output goes into the correct Tab.
    objTab = crt.GetScriptTab()
    tab = objTab.Screen  #Allows us to type "tab.xxx" instead of "objTab.Screen.xxx"
    tab.Synchronous = True
    tab.IgnoreEscape = True

    # Get the prompt of the device
    hostname = GetHostname(tab)
    
    if hostname == None:
        crt.Dialog.MessageBox("You must be in enable mode to run this script.")
    else:
        prompt = hostname + "#"

        now = datetime.datetime.now()
        mydate = now.strftime(mydatestr)
        
        # Create Filename
        filebits = [hostname, CmdName, mydate + ".txt"]
        filename = '-'.join(filebits)
        
        # Create path to save configuration file and open file
        fullFileName = os.path.join(os.path.expanduser('~'), savepath + filename)

        # Write output of command to file
        WriteOutput(SendCmd, fullFileName, prompt, tab)

    tab.Synchronous = False
    tab.IgnoreEscape = False

Main()