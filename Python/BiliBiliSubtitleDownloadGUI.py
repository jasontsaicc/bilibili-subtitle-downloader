import tkinter, threading, BiliBiliSubtitleDownload  # Import modules
import browser_cookie3


# Revision date 2024-01-22



def download_subtitles():
    if BiliBiliSubtitleDownload.cookie == BiliBiliSubtitleDownload.cookie_deprecated:
        print('【Error】 Cookie not loaded. Please log in to Bilibili in your browser and then click the corresponding browser button to load the cookie.')
        return
    if bv_number.get() == '':
        print('【Error】 BV number not entered. Please enter a BV number, such as BV13f4y1G7sA.')
        return
    download_thread = threading.Thread(target=start_download)  # Define thread to run the download program
    download_thread.start()  # Start the thread

def start_download():
    BiliBiliSubtitleDownload.download_all_subtitles(bv_number.get())

def load_firefox_cookie():
    BiliBiliSubtitleDownload.cookie = browser_cookie3.firefox()
    print('Firefox cookie loaded.')

# Callback function for radio buttons, executed when a radio button is clicked
def radio_button_callback():
    selected_encoding = encoding_var.get()
    if selected_encoding == 1:
        BiliBiliSubtitleDownload.encoding = 'utf-8'
        print('Encoding output changed to: UTF-8')
    elif selected_encoding == 2:
        BiliBiliSubtitleDownload.encoding = 'utf-16'
        print('Encoding output changed to: UTF-16')

### Tkinter GUI Window ###
window = tkinter.Tk()
window.title('BiliBiliSubtitleDownload V5')
window.geometry('400x250')

frame1 = tkinter.Frame(window)  # First section
frame2 = tkinter.Frame(window)  # Second section
frame3 = tkinter.Frame(window)  # Third section
frame4 = tkinter.Frame(window)  # Fourth section

label = tkinter.Label(window, text='BiliBiliSubtitleDownload V5', width=20, height=2, font=("Microsoft YaHei", 22))  # Label
label.pack()

frame1.pack()  # Display sections
frame2.pack()
frame4.pack()
frame3.pack()

tkinter.Label(frame1, text='Target BV Number:', width=8, height=1, font=("Microsoft YaHei", 15)).pack(side='left')  # Label
bv_number = tkinter.Entry(frame1)  # BV number input box
bv_number.pack(side='right')

encoding_var = tkinter.IntVar()  # Get the value parameter corresponding to the radio button using tk.IntVar()
radio1 = tkinter.Radiobutton(frame2, text='UTF-8     ', variable=encoding_var, value=1, command=radio_button_callback, font=("Microsoft YaHei", 15))  # Radio button
radio1.pack(side='left')
radio2 = tkinter.Radiobutton(frame2, text='UTF-16', variable=encoding_var, value=2, command=radio_button_callback, font=("Microsoft YaHei", 15))
radio2.pack(side='right')

download_button = tkinter.Button(frame3, text='Download', command=download_subtitles, width=15, height=1, font=("Microsoft YaHei", 18))  # Button
download_button.pack(side='right')

load_cookie_button = tkinter.Button(frame4, text='Load Firefox Cookie', command=load_firefox_cookie, width=15, height=1, font=("Microsoft YaHei", 18))  # Button
load_cookie_button.pack(side='right')

print('''
    ### 1. Log in to Bilibili in your browser, then click the corresponding browser button to load the cookie. Currently, only Firefox is supported.
    ### 2. Enter the BV number, such as BV13f4y1G7sA, and click the "Download" button. Wait for the download to complete.
    ### The default encoding output is UTF-8. If subtitles appear garbled in some players, try selecting UTF-16 encoding.
    ### Example BV numbers for testing: BV13f4y1G7sA, BV1XA411G7ib, BV18a4y1H73s (this one has a lot, use with caution).
''')

window.mainloop()
