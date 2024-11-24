import time
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMainWindow
from lyrics_popup import PlayListDialog
from db_functions import *
from music import Ui_MusicApp
import random
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QInputDialog, QMessageBox

from PyQt5.QtWidgets import  QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl,QTimer,Qt
import ctypes
import songs
import os

import ctypes

def get_volume():
    devices = ctypes.WinDLL('winmm.dll')
    volume = ctypes.c_uint()
    devices.waveOutGetVolume(0, ctypes.byref(volume))
    left_channel = volume.value & 0xffff  # Lower 16 bits
    right_channel = (volume.value >> 16) & 0xffff  # Upper 16 bits
    avg_volume = (left_channel + right_channel) / 2  # Average volume
    return int(avg_volume / 0xffff * 100)




class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()  
        self.setupUi(self)

        #removing default title bar
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        #done
        global stopped
        global looped 
        global is_shuffled

        stopped = False
        looped = False
        is_shuffled = False

       
        #database things
        create_database_or_database_table(' favourites')
        self.load_favourites_into_app()
        self.load_playlist

        #title bar
        self.initialPosition = self.pos()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)
        #creating player
        self.player = QMediaPlayer()

        self.curr_volume = 65
        self.player.setVolume(self.curr_volume)
        self.volume_dial.setValue(self.curr_volume)
        self.volume_label.setText(f'{self.curr_volume}')   


        #connecting button
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.volume_dial.valueChanged.connect(lambda : self.change_volume())
        self.next_btn.clicked.connect(self.next_song)
        self.stop_btn.clicked.connect(self.stop_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.loop_one_btn.clicked.connect(self.loop_one_song)
        self.delete_selected_btn.clicked.connect(self.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)
        self.loaded_songs_listWidget.itemDoubleClicked.connect(self.open_lyrics)
        self.song_list_btn.clicked.connect(self.switch_to_songs)
        self.playlists_btn.clicked.connect(self.switch_to_playlist)
        self.favourites_btn.clicked.connect(self.switch_to_favourites)

        #favourites
        self.add_to_fav_btn.clicked.connect(self.add_to_favourites)
        self.delete_selected_favourite_btn.clicked.connect(self.remove_song_from_favourites)
        self.delete_all_favourites_btn.clicked.connect(self.remove_all_songs_from_favourites)

        #playlists
        self.playlists_listWidget.itemDoubleClicked.connect(self.show_playlist_content)
        self.new_playlist_btn.clicked.connect(self.new_playlist)
        self.remove_selected_playlist_btn.clicked.connect(self.delete_playlist)
        self.remove_all_playlists_btn.clicked.connect(self.delete_all_playlists)
        self.add_to_playlist_btn.clicked.connect(self.add_all_current_songs_to_a_playlist)
        try:
            self.load_selected_playlist_btn.clicked.connect(
            lambda:self.load_playlist_songs_to_current_list(self.playlists_listWidget.currentItem().text()
            )
        )
        except Exception as e:
            print()
            
        


        self.show()


        def moveApp(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.initialPosition)
                self.initialPosition = event.globalPos()
                event.accept()
            
        self.title_frame.mouseMoveEvent = moveApp
        
    # to handle mouse position
    def mousePressEvent(self, event):
        self.initialPosition = event.globalPos()
    
    

    

    # slider 
    def move_slider(self):
        if stopped:
            return
        else:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                slider_position =  self.player.position()


                self.music_slider.setValue(slider_position)
                #print(f'Duration :{self.player.duration()}')
                #print(f'current :{slider_position}')

                current_time = time.strftime(f"%H:%M:%S",time.localtime(self.player.position()/1000))
                song_duration = time.strftime(f"%H:%M:%S",time.localtime(self.player.duration()/1000))
                self.time_label.setText(f"{current_time} / {song_duration}")

    # adding songs here
    def add_songs(self):
        files,_ = QFileDialog.getOpenFileNames(
            self,caption='add songs to the app',directory=':\\',#:\\ remebers the previous songs that are loaded
            filter='Supported Files(*.mp3;*.mpeg;*.ogg;*.m4a;*.mp4)'
        )
        if(files):
            for file in files:
                songs.current_song_list.append(file)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon('C:\\music player2\\Advanced_Music_Player_with_PyQt5-starter\\utils\\images\\music_list.png'),
                        os.path.basename(file)
                    )
                )
    #playing
    def play_song(self):
        try:
            global stopped
            stopped = False
        
            current_selection = -1
            prev_song = None
        
            if self.stackedWidget.currentIndex() == 0:
                current_selection = self.loaded_songs_listWidget.currentRow()
                if current_selection != -1:
                    prev_song = songs.current_song_list[current_selection]
            elif self.stackedWidget.currentIndex() == 2:
                current_selection = self.favourites_listWidget.currentRow()
                if current_selection != -1:
                    prev_song = songs.favourites_song_list[current_selection]

            if prev_song:
                song_url = QMediaContent(QUrl.fromLocalFile(prev_song))
                self.player.setMedia(song_url)
                self.player.play()

                self.current_song_name.setText(f'{os.path.basename(prev_song)}')
                self.current_song_path.setText(f'{os.path.dirname(prev_song)}')
            else:
                QMessageBox.warning(
                    self,
                    'Play Song',
                    'No song selected'
                )
        except Exception as e:
            print(f"play song error: {e}")

    #pause and unpause
    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
   
    def change_volume(self):
        try:
            self.curr_volume = self.volume_dial.value()
            self.player.setVolume(self.curr_volume)
        except Exception as e:
            print(f"volume change error: {e}")

    def stop_song(self):
        try:
            self.player.stop()
            self.music_slider.setValue(0)
            self.time_label.setText(f'00:00:00 / 00:00:00')
            self.current_song_name.setText(f'Song name goes here')
            self.current_song_path.setText(f'Song path goes here')
            pass
        except Exception as e:
            print(f"Stop song error {e}")

    def default_next(self):
        try:
            if self.stackedWidget.currentIndex()==0:
                current_media = self.player.media()
                current_media_url = current_media.canonicalUrl().path()[1:]
                song_index = self.loaded_songs_listWidget.currentRow()
                next_index = (song_index + 1) % len(songs.current_song_list)
                next_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)
                self.current_song_name.setText(f'{os.path.basename(next_song)}')
                self.current_song_path.setText(f'{os.path.dirname(next_song)}')

            elif self.stackedWidget.currentIndex()==2:
                current_media = self.player.media()
                current_media_url = current_media.canonicalUrl().path()[1:]
                song_index = self.favourites_listWidget.currentRow()
                next_index = (song_index + 1) % len(songs.favourites_song_list)
                next_song = songs.favourites_song_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)
                self.current_song_name.setText(f'{os.path.basename(next_song)}')
                self.current_song_path.setText(f'{os.path.dirname(next_song)}')


            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()

            
        except Exception as e:
            print(f"Default next error :{e}")

    def looped_next(self):
        try:
            current_media = self.player.media()
            current_media_url = current_media.canonicalUrl().path()[1:]
            song_index = self.loaded_songs_listWidget.currentRow()
            next_index = (song_index + 1) % len(songs.current_song_list)
            next_song = songs.current_song_list[next_index]

            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()

            # Update the UI
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')
        except Exception as e:
            print(f"looped next error: {e}")
        
    

    
    def shuffled_next(self):
        try:
            
            
            next_index = random.randint(0,len(songs.current_song_list)-1)
            next_song = songs.current_song_list[next_index]
            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')
        except Exception as e:
            print(f"shuffled next error :{e}")
        



    def next_song(self):
        try:
            global looped
            global is_shuffled

            if is_shuffled:
                self.shuffled_next()
            elif looped:
                self.looped_next()
            else:
                self.default_next()
        
        except Exception as e:
            print(f"next:{e}")
    def previous_song(self):
        try:
            current_media = self.player.media()
            current_media_url = current_media.canonicalUrl().path()[1:]
            song_index = self.loaded_songs_listWidget.currentRow()
            prev_index = song_index - 1
            prev_song = songs.current_song_list[prev_index]
            song_url = QMediaContent(QUrl.fromLocalFile(prev_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(prev_index)
            self.current_song_name.setText(f'{os.path.basename(prev_song)}')
            self.current_song_path.setText(f'{os.path.dirname(prev_song)}')
        except Exception as e:
            print(f"previous :{e}")

    def loop_one_song(self):
        try:
            global is_shuffled
            global looped

            if not looped:
                looped = True
                self.shuffle_songs_btn.setEnabled(False)
            else:
                looped = False
                self.shuffle_songs_btn.setEnabled(True)
        except Exception as e:
            print(f"Looping error : {e}")
    def shuffle_playlist(self):
        try:
            global is_shuffled
            global looped

            if not is_shuffled:
                is_shuffled = True
                self.loop_one_btn.setEnabled(False)
            else:
                is_shuffled = False
                self.loop_one_btn.setEnabled(True)
        except Exception as e:
            print(f"shuffle playlist error : {e}")
    
    def remove_selected_song(self):
        try:
            pass
        except Exception as e:
            print(f"remove selected error {e}")

    def remove_selected_song(self):
        try:
            if self.loaded_songs_listWidget.count()==0:
                QMessageBox.information(
                    self,'Remove selected song',
                    'playlist is empty'
                )
                return
            current_index = self.loaded_songs_listWidget.currentRow()
            self.loaded_songs_listWidget.takeItem(current_index)
            songs.current_song_list.pop()

        except Exception as e:
            print(f"remove selected error {e}")

    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count()==0:
                QMessageBox.information(
                    self,'Remove selected song',
                    'playlist is empty'
                )
                return
            question = QMessageBox.question(
                self,'remove all songs',
                'This action will remove all songs from list and it cannot be reversed \n',
                QMessageBox.Yes | QMessageBox.Cancel | QMessageBox.No
            )
            if question == QMessageBox.Yes:
                self.pause_and_unpause()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()
            
        except Exception as e:
            print(f"remove all error {e}")

    def switch_to_favourites(self):
        self.stackedWidget.setCurrentIndex(2)
    def switch_to_playlist(self):
        self.stackedWidget.setCurrentIndex(1)
    def switch_to_songs(self):
        self.stackedWidget.setCurrentIndex(0)
    
    #favourites functions 
    #load from fav
    def load_favourites_into_app(self):
        favourite_songs = fetch_all_songs_from_database_table(' favourites')
        songs.favourites_song_list.clear()
        self.favourites_listWidget.clear()
        for favourite in favourite_songs:
            songs.favourites_song_list.append(favourite)
            self.favourites_listWidget.addItem(
                QListWidgetItem(
                    QIcon("C:\\music player2\\Advanced_Music_Player_with_PyQt5-starter\\utils\\images\\like.png"),
                    os.path.basename(favourite)
                )
                
                )

    #add songs to fav
    def add_to_favourites(self):
        current_index = self.loaded_songs_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self,'Add songs to favourites',
                'select a song to add to favourites'
            )
            return
        try:
            
            song = songs.current_song_list[current_index]
            add_song_to_database_table(song=f"{song}",table=' favourites')
           # QMessageBox.information(
           #     self,'Add songs to favourites',
           #     f'{os.path.basename(song)} was added succesfully'
           # )
            self.load_favourites_into_app()
        except Exception as e:
            print(f"add to fav erorr {e}")
    def remove_song_from_favourites(self):
        if self.favourites_listWidget.count()==0:
                QMessageBox.information(
                    self,'Remove  song from favourite ',
                    'favourite  is empty'
                )
                return
        current_index = self.favourites_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                    self,'Remove  song from favourite ',
                    'select a song to remove from favourites'
                )
            return
        try:
            song = songs.favourites_song_list[current_index]
            delete_song_from_database_table(song=f'{song}',table=' favourites')
            self.load_favourites_into_app()
        except Exception as e:
            print(f"remove from fav error {e}")
        
    def remove_all_songs_from_favourites(self):
        if self.favourites_listWidget.count()==0:
                QMessageBox.information(
                    self,'Remove  song from favourite ',
                    'favourite  is empty'
                )
                return
        question = QMessageBox.question(
            self,'Remove all from favourites',
            'This action cannot be reverted \n'
            'Continue',
            QMessageBox.Yes | QMessageBox.No
        )
        if question == QMessageBox.Yes:
           
            try:
                delete_all_songs_from_database_table(table=' favourites')
                self.load_favourites_into_app()
            except Exception as e:
                print(f"remove all from fav error {e}")
            finally:
                self.load_favourites_into_app()
    def load_playlist(self):
        playlists = get_playlist_tables()
        self.playlists_listWidget.clear()
        for playlist in playlists:
            self.playlists_listWidget.addItem(
                QListWidgetItem(
                    QIcon("C:\\music player2\\Advanced_Music_Player_with_PyQt5-starter\\utils\\images\\dialog-music.png"),
                    playlist

                )
            )


    def new_playlist(self):
        try:
            existing = get_playlist_tables()
            name, ok = QInputDialog.getText(
                self, 'Create new playlist', 'Enter Playlist name'
            )
            if not ok or name.strip() == "":
                QMessageBox.information(self, 'Name error', 'Playlist name can\'t be empty')
                return
            else:
                if name not in existing:
                    create_database_or_database_table(f"{name}")
                    self.load_playlist()
                elif name in existing:
                    caution = QMessageBox.question(
                        self, 'Replace playlist',
                        f'Playlist with name "{name}" exists.\nDo you want to replace it?',
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if caution == QMessageBox.Yes:
                        delete_database_table(f'{name}')
                        create_database_or_database_table(f'{name}')
                        self.load_playlist()
        except Exception as e:
            print(f"Playlist creation error: {e}")
        finally:
            self.load_playlist()
    def delete_playlist(self):
        playlist = self.playlists_listWidget.currentItem().text()
        try:
            delete_database_table(playlist)
        except Exception as e:
            print(f"Deleting playlist error {e}")
        finally:
            self.load_playlist()
    def delete_all_playlists(self):
        playlists = get_playlist_tables()
        try:
            for playlist in playlists:
                delete_database_table(playlist)
        except Exception as e:
            print(f"Deleting all playlists error {e}")
        finally:
            self.load_playlist()
    def add_song_to_a_playlist(self):
        options = get_playlist_tables()
        options.insert(0,"select any")
        playlist, _ = QInputDialog.getItem(
                self,'Add song to a playlist',
                'Choose the desired playlist',
                options,
                editable = False
            )
        if playlist=='select any':
            QMessageBox.information(
                self,'Add song to a playlist','Select any playlist'
            )
            return
        try:
            current_index = self.loaded_songs_listWidget.currentRow()
            song = songs.current_song_list[current_index]

        except Exception as e:
            QMessageBox.information(
                self,'Unsuccesful','no song selected'
            )
            return
        add_song_to_database_table(song=song,table=playlist)
        self.load_playlist()

    def add_all_current_songs_to_a_playlist(self):
        options = get_playlist_tables()
        options.insert(0,"select any")
        playlist, _ = QInputDialog.getItem(
                self,'Add song to a playlist',
                'Choose the desired playlist',
                options,
                editable = False
            )
        if playlist=='select any':
            QMessageBox.information(
                self,'Add song to a playlist','Select any playlist'
            )
            return
        if len(songs.current_song_list)<1:
            QMessageBox.information(
                self,'ADD SONGS TO PLAYLIST','Song list is empty'
            )
            return
        for song in songs.current_song_list:
            add_song_to_database_table(song=song,table=playlist)
        self.load_playlist()


    def load_playlist_songs_to_current_list(self, playlist):
        try:
            playlist_songs = fetch_all_songs_from_database_table(playlist)

            if len(playlist_songs) < 1:
                QMessageBox.information(
                    self, 'Empty Playlist', 'Add songs to playlist'
                )
                return

            songs.current_song_list.clear()
            self.loaded_songs_listWidget.clear()  # Clear the current list widget items first

            for song in playlist_songs:
                songs.current_song_list.append(song)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon('C:\\music player2\\Advanced_Music_Player_with_PyQt5-starter\\utils\\images\\music_list.png'),
                        os.path.basename(song)  # Pass the song path to os.path.basename
                    )
                )

        except Exception as e:
            print(f"Loading from playlist error {playlist}: {e}")


    #def show_playlist_content(self):
    #    playlist = self.playlists_listWidget.currentItem().text()
    #    songs = fetch_all_songs_from_database_table(playlist)
    #    #print("playlist ",playlist)
    #    #print("Songs ",songs)
    #    playlist_dialog = PlayListDialog(songs,f'{playlist}')
    #    songs.cu
    #    playlist_dialog.exec_()

    def show_playlist_content(self):
        playlist = self.playlists_listWidget.currentItem().text()
        all = fetch_all_songs_from_database_table(playlist)
        
       # lyrics_dialog = PlayListDialog(all,f'{playlist}')
        songs.current_song_list.clear()
        for item in all:
            songs.current_song_list.append(item)
        for file in all:
                #songs.current_song_list.append(file)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon('C:\\music player2\\Advanced_Music_Player_with_PyQt5-starter\\utils\\images\\music_list.png'),
                        os.path.basename(file)
                    )
                )
        #self.play_song()
        #print(songs.current_song_list)
        #lyrics_dialog.exec_()
    def open_lyrics(self):
        current_index = self.loaded_songs_listWidget.currentRow()%len(songs.current_song_list)

        lyrics_dialog = PlayListDialog(f'{current_index}',f'{os.path.basename(songs.current_song_list[current_index])}')
        lyrics_dialog.exec_()


