import webbrowser
import login_credentials
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivy.uix.screenmanager import (ScreenManager, Screen, SlideTransition, FadeTransition)
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRoundFlatIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
import mysql.connector

Window.size = (300, 500)


class MyScreens(ScreenManager):
    pass


class StartPage(Screen):
    pass


class DeleteEvent(Screen):
    pass


class ImageSelectionPage(Screen):
    pass


class HomePage(Screen):
    pass


class AddEventsPage(Screen):
    pass


class ContactPage(Screen):
    pass


class Content(Screen):
    pass


class AdminSettings(Screen):
    pass


class EventError(Screen):
    pass


class DeleteDialog(Screen):
    pass

class EditEventsPage(Screen):
    pass
class EditEventForm(Screen):
    pass
class EditSelection(Screen):
    pass

class Forum2K(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events_list = []
        self.events = []
        self.db = mysql.connector.connect(user='root', password='Killeraryan1@',
                                          host='localhost',
                                          database='forum2k')
        self.csr = self.db.cursor()
        self.dialog = None
        self.emptyevents = 0

    def refresh(self):
        self.csr.execute("select id from events order by id desc limit 1")
        p = self.csr.fetchone()
        p = p if p is not None else [0]
        self.events_list = []
        if p[0] != 0:
            self.root.ids.home.ids.eventbox.clear_widgets()
            if self.emptyevents ==1:
                self.emptyevents = 0
            for i in range(1, p[0] + 1):
                self.csr.execute(f"select name,description,image,link from events where id=\"{i}\" ")
                event = self.csr.fetchone()
                event_name = event[0]
                self.events.append(event_name)
                event_description = event[1]
                blob_image = event[2]
                event_link = event[3]
                with open(f"assets/event{i}", 'wb') as file:
                    file.write(blob_image)
                event_image = f"assets/event{i}"
                self.events_list.append([event_name, event_description, event_link, event_image])
            self.root.ids.home.ids.eventbox.size = [320, 50]

            for event in self.events_list:
                event_name = event[0]
                event_description = event[1]
                event_image = event[3]
                event_link = event[2]
                self.addeventcard(event_name, event_description, event_link, event_image)
        elif self.emptyevents == 0:
            self.emptyevents = 1
            self.root.ids.home.ids.eventbox.clear_widgets()
            self.addemptyeventsbox()

    def change_screen_item(self, nav_item):
        self.root.ids.nav.switch_tab(nav_item)
        self.root.current = 'event'

    def openlink(self,link, *args):
        webbrowser.open(link)

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_hue = 'A700'
        Clock.schedule_once(self.animate, 0)
        return Builder.load_file("layout.kv")

    def gotohome(self, dt=None):
        self.root.transition = SlideTransition(direction="right")
        self.root.current = 'home'
        self.refresh()

    def gotoevent1(self, dt=None):
        self.root.transition = SlideTransition(direction="right")
        self.root.current = 'events'
    def gotoedit1(self, dt=None):
        self.root.transition = SlideTransition(direction="right")
        self.root.current = 'editform'

    def verifylogin(self, dt=None):
        username = login_credentials.admin_login[0]
        password = login_credentials.admin_login[1]
        if self.dialog.content_cls.ids.userid.text == username and self.dialog.content_cls.ids.passwd.text == password:
            self.dialog.dismiss(force=True)
            print(self.root.ids.login.ids.userid.text)
            self.root.current = "admin"
        else:
            self.dialog.content_cls.ids.error.text = "Invalid Entry\n"

    def show_confirmation_dialog(self, dt=None):

        self.dialog = MDDialog(
            title="Login",
            type="custom",
            size_hint=[0.9, None],
            content_cls=Content(),

            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color, on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK", text_color=self.theme_cls.primary_color, on_release=lambda x: self.verifylogin()
                ),
            ],
        )
        self.dialog.open()

    def show_delete_dialog(self, event_name, dt=None):
        label = MDLabel(text=f"Are you sure you want to delete the event '{event_name}'?", padding=(20, 20),
                        text_color=self.theme_cls.primary_color)
        self.dialog = MDDialog(
            title="Delete Event",
            text=f"Are you sure you want to delete event {event_name}?",
            type="custom",
            size_hint=[0.9, None],
            content_cls=DeleteDialog(),

            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color, on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="YES", text_color=self.theme_cls.primary_color, on_release=lambda x: self.delete(event_name)
                ),
            ],
        )
        self.dialog.add_widget(label)
        self.dialog.open()

    def addemptyeventsbox(self):
        card = MDCard(size_hint=(None, None), size=(250, 250), elevation=40, radius=9, md_bg_color=(0, 0, 0, 0.4),
                      padding=(10, 20), orientation="vertical")
        box = MDBoxLayout(orientation="vertical", padding=(10, 0))
        box.add_widget(
            MDLabel(text="[color=#f52891cc][size=34]Whoops![/size]\n No events ongoing but stay tuned for more!",
                    markup=True, halign='center'))
        card.add_widget(box)
        self.root.ids.home.ids.eventbox.add_widget(card)

    def verifyimage(self):
        path = self.root.ids.selection.ids.fc.selection[0]
        filename = path[path.rindex("\\") + 1:]
        if filename.endswith("jpg") or filename.endswith("jpeg") or filename.endswith("png"):
            self.root.ids.events.ids.error.text = f"{filename}\nImage uploaded"
        else:
            self.root.ids.events.ids.error.text = "Invalid file type"
    def verifyeditimage(self):
        path = self.root.ids.editselection.ids.fc.selection[0]
        filename = path[path.rindex("\\") + 1:]
        if filename.endswith("jpg") or filename.endswith("jpeg") or filename.endswith("png"):
            self.root.ids.editform.ids.error.text = f"{filename}\nImage uploaded"
            self.root.ids.editform.ids.uploaded.source =path
        else:
            self.root.ids.editform.ids.error.text = "Invalid file type"

    def animate(self, dt):
        Animation(color=(1, 1, 1, 1), duration=2).start(self.root.ids.start.ids.logo1)
        (Animation(color=(1, 1, 1, 1), duration=0.1) + Animation(size=(90, 90), duration=0.5)).start(
            self.root.ids.start.ids.logo2)
        Clock.schedule_once(self.gotohome, 2)

    def gotoselection(self, dt=None):
        self.root.current = "selection"

    def verifyevent(self):
        if self.root.ids.events.ids.event_name.text != "" and self.root.ids.events.ids.event_description.text != "":
            self.root.current = "events"
            self.addevent()
        else:
            self.root.ids.events.ids.error.text = "Please fill required fields"
    def verifyeditevent(self):
            if self.root.ids.editform.ids.event_name.text != "" and self.root.ids.editform.ids.event_description.text != "":
                self.editeventserver(self.root.ids.editform.ids.event_name.text,self.root.ids.editform.ids.event_description.text,self.root.ids.editform.ids.uploaded.source,self.root.ids.editform.ids.link.text)
                self.root.current = "home"
            else:
                self.root.ids.editform.ids.error.text = "Please fill required fields"

    def addeventcard(self, event_name, event_description, event_link, event_image):
        self.root.ids.home.ids.eventbox.size[1] += 250
        card = MDCard(size_hint=(None, None), size=(250, 250), elevation=40, radius=9, md_bg_color=(0, 0, 0, 0.4),
                      padding=(10, 20), orientation="vertical")
        card.bind(on_press=lambda x: webbrowser.open(event_link))
        box = MDBoxLayout(orientation="vertical", padding=(10, 0))
        box.add_widget(Image(source=event_image))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_name}", markup=True))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_description}", markup=True))
        card.add_widget(box)
        self.root.ids.home.ids.eventbox.add_widget(card)
    def enterquery(self,*args):
        add_data = ("insert into queries(id,name,contact,email,query)"
                    "values(%s,%s,%s,%s,%s)")
        self.csr.execute("select id from queries order by id desc limit 1")
        p = self.csr.fetchone()
        p = p if p is not None else [0]
        name=self.root.ids.home.ids.name.text
        contact=self.root.ids.home.ids.contact.text
        email=self.root.ids.home.ids.email.text
        query=self.root.ids.home.ids.query.text
        event_data = (p[0] + 1, name, contact,email,query)
        self.csr.execute(add_data, event_data)
        self.csr.execute("commit")
    def deleteevent(self):
        if len(self.events_list) == 0:
            self.show_error_dialog()
        else:
            for event in self.events_list:
                event_name = event[0]
                event_description = event[1]
                event_image = event[3]
                event_link = event[2]
                self.adddeleteeventcard(event_name, event_description, event_link, event_image)
            self.root.current = 'delete'

    def adddeleteeventcard(self, event_name, event_description, event_link, event_image):
        self.root.ids.delete.ids.deleteeventbox.size[1] += 250
        card = MDCard(size_hint=(None, None), size=(250, 250), elevation=40, radius=9, md_bg_color=(0, 0, 0, 0.4),
                      padding=(10, 20), orientation="vertical")
        card.bind(on_press=lambda x: self.show_delete_dialog(event_name))
        box = MDBoxLayout(orientation="vertical", padding=(10, 0))
        box.add_widget(Image(source=event_image))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_name}", markup=True))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_description}", markup=True))
        card.add_widget(box)
        self.root.ids.delete.ids.deleteeventbox.add_widget(card)
    def gotoedit(self):
        if len(self.events_list) == 0:
            self.show_error_dialog()
        else:
            self.root.ids.editevents.ids.editeventbox.clear_widgets()
            button=MDRoundFlatIconButton(pos_hint= {'center_x': .2, 'center_y': .95},
                                            icon= "left-arrow",
                                            text= "Go Back",
                                            on_release=lambda x:self.gotohome())
            label=MDLabel(pos_hint= {'center_x': .5, 'center_y': 0.2},
                                    text="Please select event to be edited:",
                                    font_style="Subtitle1",
                                    theme_text_color='Secondary')
            layout=MDFloatLayout()
            layout.add_widget(button)
            layout.add_widget(label)
            card=MDCard(size_hint=(None,None),
                            size=(250,130),
                            elevation=40,
                            radius=9,
                            md_bg_color=(1,1,1,1),
                            padding=(10,20),
                            orientation='vertical')
            card.add_widget(layout)
            self.root.ids.editevents.ids.editeventbox.add_widget(card)
            self.root.ids.editevents.ids.editeventbox.size=[250,180]
            for event in self.events_list:
                event_name = event[0]
                event_description = event[1]
                event_image = event[3]
                event_link = event[2]
                self.addediteventcard(event_name, event_description, event_link, event_image)
            self.root.current = 'editevents'
    def addediteventcard(self, event_name, event_description, event_link, event_image):
        self.root.ids.editevents.ids.editeventbox.size[1] += 250
        card = MDCard(size_hint=(None, None), size=(250, 250), elevation=40, radius=9, md_bg_color=(0, 0, 0, 0.4),
                      padding=(10, 20), orientation="vertical")
        card.bind(on_press=lambda x: self.editevent(event_name))
        box = MDBoxLayout(orientation="vertical", padding=(10, 0))
        box.add_widget(Image(source=event_image))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_name}", markup=True))
        box.add_widget(MDLabel(text=f"[color=#f52891cc]{event_description}", markup=True))
        card.add_widget(box)
        self.root.ids.editevents.ids.editeventbox.add_widget(card)
    def gotoeditselection(self):
        self.root.current="editselection"
    def editevent(self,event_name):
        self.root.current="editform"
        self.csr.execute(f"select * from forum2k.events where name='{event_name}'")
        event=self.csr.fetchone()
        self.id=event[0]
        self.root.ids.editform.ids.event_name.text=event[1]
        self.root.ids.editform.ids.event_description.text=event[2]
        self.root.ids.editform.ids.link.text=event[4]
        with open(f"assets/event{event[0]}", 'wb') as file:
            file.write(event[3])
        self.root.ids.editform.ids.uploaded.source=f"assets/event{event[0]}"



    def addevent(self):
        event_name = self.root.ids.events.ids.event_name.text
        event_description = self.root.ids.events.ids.event_description.text
        link = self.root.ids.events.ids.link.text
        self.csr.execute(f"Select count(name) from events where name='{event_name}'")
        q = self.csr.fetchone()[0]
        if q != 0:
            self.root.ids.events.ids.error.text = "Event Already Exists!"
        else:
            add_data = ("insert into events(id,name,description,image,link)"
                        "values(%s,%s,%s,%s,%s)")
            self.csr.execute("select id from events order by id desc limit 1")
            p = self.csr.fetchone()
            p = p if p is not None else [0]
            with open(self.root.ids.selection.ids.fc.selection[0], 'rb') as imagefile:
                image = imagefile.read()
            event_data = (p[0] + 1, event_name, event_description, image, link)
            self.csr.execute(add_data, event_data)
            self.csr.execute("commit")
            self.gotohome()
            self.refresh()

    def show_error_dialog(self):
        self.dialog = MDDialog(
            title="Error",
            text="No Events Found!",
            buttons=[
                MDFlatButton(
                    text="Go Back", text_color=self.theme_cls.primary_color, on_press=lambda x: self.gotoadmin(),
                    on_release=lambda x: self.dialog.dismiss(),
                ),
            ],
        )
        self.dialog.open()

    def gotoadmin(self, dt=None):
        self.root.current = 'admin'

    def delete(self, event_name):
        self.csr.execute(f"delete from events where name='{event_name}'")
        self.csr.execute("commit")
        self.csr.execute(
            "CREATE TABLE forum2k.eventcopy AS SELECT ROW_NUMBER() OVER() AS id,name,description,image,link FROM forum2k.events")
        self.csr.execute("Drop Table events")
        self.csr.execute("RENAME table eventcopy To events")
        self.csr.execute("commit")
        self.root.ids.delete.ids.deleteeventbox.size[1] -= 250
        self.root.ids.home.ids.eventbox.size = [320, 300]
        self.refresh()
        self.dialog.dismiss()
        self.deleteevent()
        self.gotoadmin()
    def editeventserver(self,event_name, event_description, event_image, event_link):
        with open(event_image, 'rb') as imagefile:
            image = imagefile.read()

        self.csr.execute(f"Delete from events WHERE id = '{self.id}';")

        add_data = ("insert into events(id,name,description,image,link)"
                        "values(%s,%s,%s,%s,%s)")
        event_data = (self.id, event_name, event_description, image, event_link)
        self.csr.execute(add_data, event_data)
        self.csr.execute("commit")
        self.refresh()
        self.root.current="admin"
if __name__ == '__main__':
    Forum2K().run()
