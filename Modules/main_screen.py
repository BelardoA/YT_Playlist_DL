import tkinter
import logging

from typing import Optional
from tkinter import messagebox, filedialog
from os.path import exists
from Modules.functions import PlaylistDownloader, clean_dir

window = tkinter.Tk()
window.title("Playlist Downloader")
window.geometry("600x350")
window.configure(bg="#333333")
window.resizable(False, False)
var = tkinter.StringVar()
path_status = tkinter.StringVar()
path_status.set("❌")
FONT = ("Arial", 16)
logger = logging.getLogger(__name__)


def browse_files():
    """
    function to update the filepath status and
    submit button functionality
    """
    global file_path
    file_path = filedialog.askdirectory(initialdir="/", title="Select a Folder")
    # Change label contents
    var.set(file_path)
    if exists(file_path) is True:
        path_status.set("✔️")
        path_check.config(fg="#00FF00")
        submit_btn.config(state="normal")
    else:
        path_status.set("❌")
        path_check.config(fg="#FF0000")
        submit_btn.config(state="disabled")


def start_dl(pl_link: Optional[str] = None, output_dir: Optional[str] = None):
    """
    start the process of downloading the playlist
    """
    pl_link = pl_link or pl_link_input.get()
    output_dir = output_dir or file_path_input.get()
    if pl_link != "" and output_dir != "":
        # Find the index of '&app='
        pp_index = pl_link.find("&pp=")
        # If '&app=' is found, return the substring before it
        if pp_index != -1:
            pl_link = pl_link[:pp_index]
        logger.info("Getting video count...")
        pl_downloader = PlaylistDownloader(pl_link=pl_link, output_dir=output_dir)
        # TODO: implement pop up message for user to authenticate the session
        messagebox.showinfo(
            title="Please authenticate the session!",
            message=pl_downloader.youtube.get_auth_url(),
        )
        threads = pl_downloader.total_tracks
        logger.info(f"Starting {threads} download(s)...")
        pl_downloader.run()
        clean_dir()
        logger.info("Showing completion message...")
        messagebox.showinfo(
            title="Mission Complete!",
            message="Playlist has been downloaded. {} tracks".format(threads)
            + " have been downloaded.",
        )
    else:
        logger.error("Information Missing!")
        messagebox.showerror(
            title="Information Missing!",
            message="Please verify the necessary information" + " has been provided.",
        )


def quit_app():
    """
    function to terminate the window and
    terminate the program
    """
    logger.info("Quitting application...")
    window.destroy()
    exit()


def close_window():
    """
    function to close the window and
    proceed to the next part of the main script
    """
    logger.info("Closing window...")
    window.destroy()


def start_window():
    """
    function to start the program window
    """
    logger.info("Starting GUI...")
    frame = tkinter.Frame(bg="#333333")
    global file_path_input
    global pl_link_input
    global path_check
    global submit_btn
    header_label = tkinter.Label(
        frame,
        text="YouTube Playlist MP3 Downloader",
        bg="#333333",
        fg="#FF5F15",
        font=("Arial", 30),
    )
    pl_link_label = tkinter.Label(
        frame, text="Playlist Link:", bg="#333333", fg="#FFFFFF", font=FONT
    )
    pl_link_input = tkinter.Entry(frame, font=FONT)
    path_check = tkinter.Label(
        frame, textvariable=path_status, font=FONT, bg="#333333", fg="#FF0000"
    )
    file_path_input = tkinter.Entry(
        frame, textvariable=var, font=FONT, state="disabled"
    )
    button_explore = tkinter.Button(frame, text="Save Location", command=browse_files)
    submit_btn = tkinter.Button(
        frame,
        text="Start",
        bg="#FF5F15",
        fg="#FFFFFF",
        font=FONT,
        command=start_dl,
        state="disabled",
    )
    cancel_btn = tkinter.Button(
        frame,
        text="Quit",
        bg="#FF0000",
        fg="#FFFFFF",
        font=FONT,
        command=quit_app,
    )
    header_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=20, padx=20)
    button_explore.grid(row=1, column=0)
    file_path_input.grid(row=1, column=1, pady=20, padx=20)
    path_check.grid(row=1, column=2, padx=1)
    pl_link_label.grid(row=2, column=0, padx=20)
    pl_link_input.grid(row=2, column=1, pady=20)
    submit_btn.grid(row=3, column=0, padx=40)
    cancel_btn.grid(row=3, column=1, columnspan=2, pady=30)
    frame.pack()

    window.mainloop()


if __name__ == "__main__":
    start_dl(
        "https://www.youtube.com/watch?v=TyIqEFN7k2s&list=PLWm0sL3_hdvwgPmZ3Icm7lASidbCjFWs0&pp=iAQB",
        "/home/virus/Documents/Python/YT_Playlist_DL/downloads",
    )
