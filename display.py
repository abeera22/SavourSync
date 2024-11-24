""" PROJECT 2 DISPLAY

This module uses a Graphic User Interface to input, perform computations on, and output the data.

Copyright and Usage Information
===============================

This file is Copyright Abeera Fatima and Amal Nouman Irshad.
"""

from doctest import master
from tkinter import *
from data import *
import random
from typing import Any

root = Tk()
root.title("SavourSync")

root.geometry("1100x400")

large_font = ('Helvetica', 24, 'bold')
label_large = Label(root, text="SavourSync", font=large_font)


def title_page():
    label_large.pack(pady=20)

    def new() -> None:
        """ Handles the case where a new user is using the program
        """
        clear_screen()
        userid = random.randint(1000, 999999)
        while userid in g.vertices:
            userid = random.randint(1000, 999999)
        Label(root, text=f'Your userid is {userid}. You can use this to log in in the future and access your '
                         f'saved matches.').pack()
        user = g.add_vertex(userid)
        g.save_to_json(str(userid))
        Button(root, text='Return', command=lambda: home_page(userid), padx=50).pack()

    def returning() -> None:
        """ Handles the case where a returning user is using the program
        """
        clear_screen()
        Label(root, text='Enter your userid').pack()
        e = Entry(root, width=50)
        e.pack()

        def got_id() -> None:
            """ Code to be executed once the user inputs their id.
            """
            userid = int(e.get())
            try:
                g.load_from_json(str(userid))
            except FileNotFoundError:
                Label(root, text='Userid not found in database. Please enter a valid userid.').pack()

            g.load_from_json(str(userid))

            home_page(userid)

        Button(root, text="Enter", command=got_id).pack()
        Button(root, text="Back", command=ron).pack()

    def ron() -> None:
        """ Inputs whether the user is new or returning and handles each case via their respective buttons
        """
        clear_screen()
        Label(root, text='Are you a new or returning user?').pack()
        Button(root, text="Returning", command=returning).pack()
        Button(root, text="New", command=new).pack()

    ron()

    root.mainloop()


def clear_screen() -> None:
    """ Removes all widgets on the screen except for the logo.
    """
    for widget in root.winfo_children():
        if widget is not label_large:
            widget.pack_forget()


def click_explore(label: Any, orderbutton: Any, explorebutton: Any, userid: Any) -> None:
    """ Displays the recommendations based on the users matches, if any.
    """
    orderbutton.pack_forget()
    explorebutton.pack_forget()
    label.pack_forget()
    if g.vertices[userid].neighbours == {}:
        Label(root, text='You have no matches yet. Once you order a certain item repeatedly, you will be matched with '
                         'users who share food preferences with you and can explore what new orders they have been'
                         ' trying!').pack()

    else:
        user2 = g.vertices[userid]  # user2 is the VERTEX item representing our current user
        recs = {}  # {12345: [(restaurant, cuisine), rating], 4: (restaurant, cuisine, rating)}
        # {2: [(mcdonalds, american), 4.5]}
        # rate_so_far = 4
        for match in user2.neighbours:
            for order in match.one_time_orders:
                if user2.neighbours[match] == order[1]:
                    if order not in user2.one_time_orders and order not in user2.repeated_orders:
                        value = True
                        for x in list(recs.keys()):
                            if order == recs[x][0]:
                                value = False
                                rate_so_far = int(recs[x][1])
                                if x > 1000:
                                    recs.pop(x)
                                    recs[2] = [order, (rate_so_far + int(match.one_time_orders[order])) / 2]
                                    break
                                else:
                                    recs.pop(x)
                                    recs[x + 1] = [order, (rate_so_far + int(match.one_time_orders[order])) / 2]
                                    break
                        if value:
                            recs[match.item] = [order, match.one_time_orders[order]]
        if recs == {}:
            Label(root, text='Your matches have not tried anything new lately').pack()
        else:
            for x in recs:
                if x < 1000:
                    if recs[x][1] == 'Not given':
                        Label(root, text=f'{x} of your matches tried {recs[x][0][1]} food from {recs[x][0][0]}').pack()
                    else:
                        Label(root,
                              text=f'{x} of your matches tried {recs[x][0][1]} food from {recs[x][0][0]} and on average'
                                   f' rated it {recs[x][1]} out of 5.').pack()
                else:
                    if recs[x][1] == 'Not given':
                        Label(root, text=f'User {x} tried {recs[x][0][1]} food from {recs[x][0][0]}').pack()
                    else:
                        Label(root,
                              text=f'User {x} tried {recs[x][0][1]} food from {recs[x][0][0]} and rated it {recs[x][1]}'
                                   f' out of 5.').pack()
    Button(root, text='Return', command=lambda: home_page(userid), padx=50).pack()


def click_order(userid: Any) -> None:
    """ Executes the path to be followed when a user chooses to order.
    """
    clear_screen()
    open_menu(userid)


def open_menu(userid: Any) -> None:
    """ Essentially a continuation of the click_order function. Opens a new window with the menu and prompts the user
    to choose a restaurant.
    """
    clear_screen()
    newWindow = Toplevel(master)

    newWindow.title("Menu")

    scrollable_frame = Frame(newWindow)
    scrollable_frame.pack(fill=BOTH, expand=YES)

    scrollbar = Scrollbar(scrollable_frame, orient=VERTICAL)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas = Canvas(scrollable_frame, yscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=YES)
    scrollbar.config(command=canvas.yview)

    scrollable_content = Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_content, anchor=NW)

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_content.bind("<Configure>", update_scroll_region)

    for x in menu:
        if any({x in k for k in [key for dictionary in [y.repeated_orders for y in g.vertices.values()] for key in
                                 dictionary.keys()]}):
            label = Label(scrollable_content, text=x)
            label.pack()

    l1 = Label(root, text='Choose your restaurant from the Menu')
    l1.pack()
    Label(root, text='Please make sure to close the menu window before you click enter.').pack()
    e = Entry(root, width=50)
    e.pack()

    def got_restaurant() -> None:
        """ Executes the path to be followed when a user enters a restaurant.
        """
        restaurant = e.get()
        l2 = Label(root, text='Please choose a valid restaurant from the given options')
        if restaurant not in menu:
            l2 = Label(root, text='Please choose a valid restaurant from the given options')
            l2.pack()
        else:
            clear_screen()
            Label(root, text='Choose your cuisine').pack()

            def got_cuisine() -> None:
                """ Executes the path to be followed when a user chooses a cuisine.
                """
                clear_screen()
                cuisine = list(menu[restaurant])[0]
                Label(root, text='Your food is being delivered. Please wait.').pack()

                def get_rating() -> None:
                    """ Prompts the user to enter their rating
                    """
                    Label(root, text='Rate your food on a scale of 0 to 5 inclusive').pack()
                    e2 = Entry(root, width=50)
                    e2.pack()

                    def got_rating() -> None:
                        """ Executes the path to be followed when a user inputs a rating. Prints out corresponding
                        error messages as well.
                        """
                        rating = (e2.get())
                        if not rating.isnumeric():
                            Label(root, text='Your rating must be a number.').pack()
                        elif int(rating) > 5 or int(rating) < 0:
                            Label(root, text='Your rating must be between 0 and 5 inclusive.').pack()
                        else:
                            g.vertices[userid].add_order(restaurant, cuisine, rating)
                            new_matches = []
                            for vertex in g.vertices:
                                if not g.adjacent(vertex, userid) and vertex != userid:
                                    matched_cuisine_list = [(tuple(a)[1]) for a in g.vertices[vertex].repeated_orders
                                                            for
                                                            b in
                                                            g.vertices[userid].repeated_orders if a == b]
                                    if matched_cuisine_list:
                                        matched_cuisine = matched_cuisine_list[0]
                                        new_matches.append(vertex)
                                        g.add_edge(vertex, userid, matched_cuisine)

                            g.save_to_json(str(userid))

                            if len(new_matches) == 0:
                                clear_screen()
                                home_page(userid)
                            else:
                                clear_screen()
                                match_made(new_matches, restaurant, cuisine, userid)

                    Button(root, text='Enter', command=got_rating).pack()

                label.after(1000, get_rating)

            Button(root, text=list(menu[restaurant])[0], command=got_cuisine).pack()
            Button(root, text="Back", command=lambda: open_menu(userid)).pack()

    b1 = Button(root, text="Enter", command=got_restaurant)
    b1.pack()
    Button(root, text="Back", command=lambda: home_page(userid)).pack()


def home_page(userid: Any) -> None:
    """ Returns the display to the home page.
    """
    g.save_to_json(str(userid))
    clear_screen()
    label_small = Label(root, text="If you know what you would like to order, press order. If you want to explore new"
                                   " options and see what your matches have been trying out, press explore!", )
    label_small.pack(padx=20)

    orderButton = Button(root, text='Order',
                         command=lambda: click_order(userid),
                         padx=50)
    orderButton.pack()

    exploreButton = Button(root, text='Explore', command=lambda: click_explore(label_small, orderButton, exploreButton,
                                                                               userid), padx=50)
    exploreButton.pack()


def match_made(new_matches: Any, restaurant: Any, cuisine: Any, userid: Any) -> None:
    """ Executes the path to be followed once a match(es) is/are made. It displays the match to the user and gives them
    the choice to remove the match or return home.
    """
    if len(new_matches) == 1:
        Label(root, text=f'You made a new match! You will now receive recommendations based on the choices of '
                         f'User {new_matches[0]}').pack()
    elif len(new_matches) == 2:
        Label(root, text=f'You made 2 new matches! You will now receive recommendations based on the choices '
                         f'of User {new_matches[0]} and user {new_matches[1]}').pack()
    else:
        Label(root, text=f'You made some new matches! You will now receive recommendations based on the choices of '
                         f'User {new_matches[0]}, User {new_matches[1]}, and {len(new_matches) - 2} others').pack()

    Label(root, text='If you want to remove this/these user(s) as a match, press remove. To return to the main '
                     'MENU, press return').pack()

    def remove_match(restaurant: Any, cuisine: Any, userid: Any) -> None:
        """ It removes the match that has been made based on the given order and allows the user to return to the home
        screen.
        """
        clear_screen()
        for x in new_matches:
            g.remove_edge(userid, x)
        g.vertices[userid].repeated_orders.pop((restaurant, cuisine))
        Label(root, text='This/these user(s) have been removed as matches. You will not receive recommendations '
                         'based on their orders').pack()
        Button(root, text='Return', command=lambda: home_page(userid), padx=50).pack()

    Button(root, text='Return', command=lambda: home_page(userid), padx=50).pack()
    Button(root, text='Remove', command=lambda: remove_match(restaurant, cuisine, userid),
           padx=50).pack()


if __name__ == '__main__':
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136'],
        'extra-imports': ['master', 'tkinter', 'project_2_data', 'random'],
        'max-nested-blocks': 8
    })