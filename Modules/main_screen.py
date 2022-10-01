import tkinter
from tkinter import messagebox, filedialog
from os.path import exists
from Modules.threads import start_threads
from Modules.functions import get_channel, get_vid_count, clean_dir

window = tkinter.Tk()
window.title("Playlist Downloader")
window.geometry('600x350')
window.configure(bg='#333333')
window.resizable(False, False)
var = tkinter.StringVar()
path_status = tkinter.StringVar()
path_status.set("❌")


def browseFiles():
    """
    function to update the filepath status and
    submit button functionality
    """
    global file_path
    file_path = filedialog.askdirectory(
        initialdir="/",
        title="Select a Folder")
    # Change label contents
    var.set(file_path)
    if exists(file_path) is True:
        path_status.set("✔️")
        path_check.config(
            fg="#00FF00"
        )
        submit_btn.config(state='normal')
    else:
        path_status.set("❌")
        path_check.config(
            fg="#FF0000"
        )
        submit_btn.config(state='disabled')


def start_dl():
    """
    start the process of downloading the playlist
    """
    pl_link = pl_link_input.get()
    output_dir = file_path_input.get()
    if pl_link != '' and output_dir != '':
        get_channel(
            pl_link=pl_link)
        threads = get_vid_count(
            pl_link=pl_link)
        start_threads(
            thread_cnt=threads,
            pl_link=pl_link,
            file_path=output_dir
        )
        clean_dir()
        messagebox.showinfo(
            title="Mission Complete!",
            message="Playlist has been downloaded. {} tracks".format(
                threads
            ) + ' have been downloaded.')
    else:
        messagebox.showerror(
            title="Information Missing!",
            message="Please verify the necessary information"
            + " has been provided."
        )


def quit_app():
    """
    function to terminate the window and
    terminate the program
    """
    window.destroy()
    exit()


def close_window():
    """
    function to close the window and
    proceed to the next part of the main script
    """
    window.destroy()


def start_window():
    """
    function to start the program window
    """
    frame = tkinter.Frame(bg='#333333')
    global file_path_input
    global pl_link_input
    global path_check
    global submit_btn
    header_label = tkinter.Label(
        frame,
        text="YouTube Playlist Downloader",
        bg="#333333",
        fg="#FF5F15",
        font=("Arial", 30)
    )
    pl_link_label = tkinter.Label(
        frame,
        text="Playlist Link:",
        bg="#333333",
        fg="#FFFFFF",
        font=("Arial", 16)
    )
    pl_link_input = tkinter.Entry(
        frame,
        font=("Arial", 16)
    )
    path_check = tkinter.Label(
        frame,
        textvariable=path_status,
        font=("Arial", 16),
        bg="#333333",
        fg="#FF0000"
    )
    file_path_input = tkinter.Entry(
        frame,
        textvariable=var,
        font=("Arial", 16),
        state="disabled"
    )
    button_explore = tkinter.Button(
        frame,
        text="Save Location",
        command=browseFiles)
    submit_btn = tkinter.Button(
        frame,
        text="Start",
        bg="#FF5F15",
        fg="#FFFFFF",
        font=("Arial", 16),
        command=start_dl,
        state="disabled"
    )
    cancel_btn = tkinter.Button(
        frame,
        text="Quit",
        bg="#FF0000",
        fg="#FFFFFF",
        font=("Arial", 16),
        command=quit_app
    )
    header_label.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="news",
        pady=20,
        padx=20
    )
    button_explore.grid(
        row=1,
        column=0
    )
    file_path_input.grid(
        row=1,
        column=1,
        pady=20,
        padx=20
    )
    path_check.grid(
        row=1,
        column=2,
        padx=1
    )
    pl_link_label.grid(
        row=2,
        column=0,
        padx=20
    )
    pl_link_input.grid(
        row=2,
        column=1,
        pady=20
    )
    submit_btn.grid(
        row=3,
        column=0,
        padx=40
    )
    cancel_btn.grid(
        row=3,
        column=1,
        columnspan=2,
        pady=30
    )
    frame.pack()

    window.mainloop()
