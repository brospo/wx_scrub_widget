import wx
import wx.lib.inspection
import ObjectListView as lv
from Data import Data


class ScrubLabelEvent(wx.PyCommandEvent):
    def __init__(self, evtType, _id):
        """
        The event sent when a ScrubLabel is scrubbed.
        """
        wx.PyCommandEvent.__init__(self, evtType, _id)
        self.delta = 0
        self.cmd_down = False

    def get_delta(self):
        """
        :return: The distance between the mouse event and its anchor point.
        """
        return self.delta

    def increasing(self):
        if self.delta > 0:
            return True
        else:
            return False

    def decreasing(self):
        if self.delta < 0:
            return True
        else:
            return False

    def CmdDown(self):
        return self.cmd_down


class ScrubLabel(wx.StaticText):
    myEVT_LABEL_SCRUBBED = wx.NewEventType()
    EVT_LABEL_SCRUBBED = wx.PyEventBinder(myEVT_LABEL_SCRUBBED, 1)


    def __init__(self, _parent, _id, _value, _scroll_horz=True, *args, **kwds):
        """
        A label that will hold the mouse in place when left clicked, allowing it to be scrubbed
        either left or right (up or down)
        :param _parent: The container that
        :param _id: A unique wxpython ID
        :param _value: The text that is going to be displayed
        """
        wx.StaticText.__init__(self, _parent, _id, str(_value), *args, **kwds)

        self.parent = _parent

        if _scroll_horz:
            self.scroll_dir = 0
        else:
            self.scroll_dir = 1

        self.cur_value = _value

        # Flag that is true if a drag is happening after a left click
        self.changing_value = False

        # The point in which the cursor gets anchored to during the drag event
        self.anchor_point = (0, 0)

        self.Bind(wx.EVT_MOTION, self._on_mouse_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down, self)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up, self)

    def _on_mouse_motion(self, event):
        """
        When the mouse moves, it check to see if it is a drag, or if left down had happened.
        If neither of those cases are true then it will cancel the action.
        If they are true then it calculates the change in position of the mouse, then changes
        the position of the cursor back to where the left click event happened.
        """
        # Changes the cursor
        if self.changing_value:
            self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
        else:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

        # Calculate the change in mouse position
        cur_point = event.GetPosition()
        delta = cur_point[self.scroll_dir] - self.anchor_point[self.scroll_dir]

        # If the cursor is being moved and dragged left or right over the label
        if delta != 0 and event.Dragging() and self.changing_value:

            # Set the parameters of the event that will be posted
            evt = ScrubLabelEvent(ScrubLabel.myEVT_LABEL_SCRUBBED, self.GetId())
            evt.SetEventObject(self)
            evt.delta = delta
            evt.cmd_down = event.CmdDown()
            # Send out the event
            self.GetEventHandler().ProcessEvent(evt)

        if event.Dragging() and self.changing_value:
            self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
            # Set the cursor back to the original point so it doesn't run away
            self.WarpPointer(self.anchor_point[0], self.anchor_point[1])

        # Case where the mouse is moving over the control, but has no
        # intent to actually change the value
        if self.changing_value and not event.Dragging():
            self.changing_value = False
            self.parent.SetDoubleBuffered(False)

    def _on_left_up(self, event):
        """
        Cancels the changing event, and turns off the optimization buffering
        """
        self.changing_value = False
        self.parent.SetDoubleBuffered(False)
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def _on_left_down(self, event):
        """
        Sets the anchor point that the cursor will go back to (the middle of the scrube label.
        Also turns on the doublebuffering which eliminates the flickering when rapidly changing
        values.
        """
        width, height = self.GetSizeTuple()

        self.anchor_point = (width/2, height/2)
        self.changing_value = True
        self.parent.SetDoubleBuffered(True)

    def _on_win_leave(self, event):
        """
        In the event that the mouse is moved fast enough to leave the bounds of the label, this
        will be triggered, warping the cursor back to where the left click event originally
        happened
        """
        if self.changing_value:
            self.WarpPointer(self.anchor_point[0], self.anchor_point[1])

    def set_label(self, _label):
        """
        Wrapper for setting the label, which allows a non string object to be set.
        """
        self.SetLabel(str(_label))
        self.cur_value = _label


#  Define Dynamic Test Drop Target class
class DynDropTarget(wx.TextDropTarget):
    """ This object implements Drop Target functionality for Text """
    def __init__(self, _frame, _dyn_sent, _id):
        """ Initialize the Drop Target, passing in the Object Reference to
            indicate what should receive the dropped text """
        #  Initialize the wx.TextDropTarget Object
        wx.TextDropTarget.__init__(self)

        # The frame that is used to contain the drag and drops
        self.frame = _frame
        self.dyn_sentence = _dyn_sent

        #  Store the Object Reference for dropped text
        self.obj_id = _id

    def OnDropText(self, x, y, data):
        """ Implement Text Drop """
        #  When text is dropped, write it into the object specified
        source_id = int(data.split()[0])
        source_index = int(data.split()[1])

        source = self.frame.FindWindowById(source_id)
        to_set = source.GetObjectAt(source_index).data
        self.dyn_sentence.new_scrub_vals(self.obj_id, to_set)


class ClickLabel(wx.StaticText):
    def __init__(self,  _parent, _id, _value, *args, **kwds):
        """
        Simple wrapper for a statictext. The actual changing of the label is NOT handled here.
        Allows for the setting (and storing) of a value that is not just a string
        :param _parent: The parent that it is contained within
        :param _id: The wx id for this object
        :param _value: The value to display
        """
        wx.StaticText.__init__(self, _parent, _id, str(_value), *args, **kwds)

        self.cur_value = _value

        self.Bind(wx.EVT_ENTER_WINDOW, self._on_win_enter)

    def _on_win_enter(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def set_label(self, _label):
        """
        Wrapper for setting the label, which allows a non string object to be set.
        """
        self.SetLabel(str(_label))
        self.cur_value = _label


class DynamicSentence(wx.WrapSizer):
    def __init__(self, _frame, _parent):
        """
        A 'paragraph' style combination of scrub labels, and static text. The order that they are
        displayed the same as the order in which that they are added to the control.
        :param _parent: The parent that contains the control
        """
        wx.WrapSizer.__init__(self, wx.HORIZONTAL)
        _parent.SetSizer(self)

        self.frame = _frame
        self.parent = _parent
        self.change_rate = 1.0

        self.change_value = 0

        self.dyn_text_vals = {}
        self.dyn_text = []
        self.static_text = []
        self.sentence = []

    def clear(self):
        """
        Erases the whole sentence
        """
        self.dyn_text_vals = {}
        self.dyn_text = []
        self.static_text = []
        self.sentence = []

    def delete_word(self):
        """
        Deletes the last item in the list from the sentence.
        """
        to_delete = self.sentence.pop()
        to_delete.Hide()

        if to_delete in self.static_text:
            self.static_text.remove(to_delete)
            return
        elif to_delete in self.dyn_text:
            self.dyn_text.remove(to_delete)
            key = to_delete.GetId()
            del self.dyn_text_vals[key]

        self.Layout()

    def add_text(self, _text, split_words=True):
        """
        Adds a static text next in the sequence.
        :param _text: The text that will be displayed.
        """
        if split_words:
            words = _text.split()
            words[0] = ' ' + words[0]
            for word in words:
                to_add = wx.StaticText(self.parent, wx.ID_ANY, word + ' ')
                self.static_text.append(to_add)
                self.sentence.append(to_add)
                self.Add(to_add)
        else:
            to_add = wx.StaticText(self.parent, wx.ID_ANY, _text)
            self.static_text.append(to_add)
            self.sentence.append(to_add)
            self.Add(to_add)

        self.Layout()

    def add_scrubber(self, _values, _default_value, scroll_horz=True, can_drop=False):
        """
        :param _values: A list of values that will be scrubbed through
        :param _default_value: A value from _values that will be displayed initially
        """
        _id = wx.NewId()
        self.dyn_text_vals[_id] = _values
        to_add = ScrubLabel(self.parent, _id, _default_value, _scroll_horz=scroll_horz)

        # Add to local dynamic text list, and to the sizer
        self.dyn_text.append(to_add)
        self.sentence.append(to_add)
        self.Add(to_add)

        to_add.Bind(ScrubLabel.EVT_LABEL_SCRUBBED, self._value_scrubbed)

        # Must call layout anytime a control is made or modified.
        self.Layout()

        if can_drop:
            drop_tar = DynDropTarget(self.frame, self, _id)
            to_add.SetDropTarget(drop_tar)

        return to_add

    def add_clicker(self, _values, _default_value, can_drop=False):

        _id = wx.NewId()
        self.dyn_text_vals[_id] = _values
        to_add = ClickLabel(self.parent, _id, _default_value)

        self.dyn_text.append(to_add)
        self.sentence.append(to_add)
        self.Add(to_add)
        self.Layout()

        to_add.Bind(wx.EVT_LEFT_DOWN, self._value_clicked)

        if can_drop:
            drop_tar = DynDropTarget(self.frame, self, _id)
            to_add.SetDropTarget(drop_tar)

    def _value_clicked(self, event):
        _id = event.GetId()
        cur_text = event.GetEventObject()
        cur_index = self.dyn_text_vals[_id].index(cur_text.cur_value)

        # Always goes down through the list, so it will cycle back from the end
        to_set = self.dyn_text_vals[_id][cur_index - 1]
        cur_text.set_label(to_set)

        # IMPORTANT is what aligns everything
        self.Layout()

        # Allows the event to propagate further up to anyone whos listening
        event.Skip()

    def _value_scrubbed(self, event):
        """
        Private function, is listening for when a control is scrubbed, as to change its cursor
        left or right in the list of values that is associated with the control.
        :param event: The event given by the event
        """
        _id = event.GetId()
        cur_text = event.GetEventObject()
        cur_index = self.dyn_text_vals[_id].index(cur_text.cur_value)

        # If cmd is down, slow the change rate to 1/10 of the current value
        if event.CmdDown():
            self.change_value += self.change_rate/10.0
        else:
            self.change_value += self.change_rate

        # Only if the floating point change value gets to the first integer value
        if self.change_value >= 1:

            # Try to avoid any index error on the high end
            try:
                # Decide to move up in the index
                if event.increasing():
                    to_set = self.dyn_text_vals[_id][cur_index + 1]
                    cur_text.set_label(to_set)
                else:

                    # Check to see if negative (if it is it would not throw an exception,
                    # rather start from the other end of the list)
                    if (cur_index - 1) >= 0:
                        to_set = self.dyn_text_vals[_id][cur_index - 1]
                        cur_text.set_label(to_set)
            except IndexError:
                # Hit the edge of the list
                pass

            # Reset the change value since the value was just changed.
            self.change_value = 0

        # IMPORTANT is what aligns everything
        self.Layout()

        # Allows the event to propagate further up to anyone whos listening
        event.Skip()

    def new_scrub_vals(self, _id, vals):
        """
        Updates the values for an existing scrub control
        :param _id: The wxID of the control
        :param vals: A list of string convertible items
        """
        if _id in self.dyn_text_vals and type(vals) == list and len(vals) > 0:
            self.dyn_text_vals[_id] = vals
            print self.frame.FindWindowById(_id)

            scrub_label = self.frame.FindWindowById(_id)
            scrub_label.set_label(vals[0])

        elif _id in self.dyn_text_vals:
            list_vals = [vals]
            self.dyn_text_vals[_id] = list_vals

            scrub_label = self.frame.FindWindowById(_id)
            scrub_label.set_label(list_vals[0])
        self.Layout()

    def set_static_font(self, *args, **kwargs):
        """
        Iterates through all static text and changes its font.
        """
        for text in self.static_text:
            text.SetFont(*args, **kwargs)

        self.Layout()

    def set_dyn_font(self, *args, **kwargs):
        """
        Iterates through the dynamic elements and calls their setfont function.
        """
        for text in self.dyn_text:
            text.SetFont(*args, **kwargs)

        self.Layout()


# Below is all for testing
# ----------------------------------------------------------------------------------------
class ProportionalSplitter(wx.SplitterWindow):
        def __init__(self, parent, _id=-1, proportion=0.66, size=wx.DefaultSize, **kwargs):
                wx.SplitterWindow.__init__(self, parent, _id, wx.Point(0, 0), size, **kwargs)

                # the minimum size of a pane.
                self.SetMinimumPaneSize(50)
                self.proportion = proportion
                if not 0 < self.proportion < 1:
                        raise ValueError("proportion value for ProportionalSplitter "
                                         "must be between 0 and 1.")
                self.ResetSash()
                self.Bind(wx.EVT_SIZE, self.OnReSize)
                self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged, id=_id)
                # # hack to set sizes on first paint event
                self.Bind(wx.EVT_PAINT, self.OnPaint)
                self.firstpaint = True

        def SplitHorizontally(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitHorizontally(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetHeight() * self.proportion)))

        def SplitVertically(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitVertically(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetWidth() * self.proportion)))

        def GetExpectedSashPosition(self):
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(), self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(), self.GetParent().GetClientSize().width)
                return int(round(tot * self.proportion))

        def ResetSash(self):
                self.SetSashPosition(self.GetExpectedSashPosition())

        def OnReSize(self, event):
                """
                Window has been resized, so we need to adjust the sash based on self.proportion.
                """
                self.ResetSash()
                event.Skip()

        def OnSashChanged(self, event):
                """
                We'll change self.proportion now based on where user dragged the sash.
                """
                pos = float(self.GetSashPosition())
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(), self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(), self.GetParent().GetClientSize().width)
                self.proportion = pos / tot
                event.Skip()

        def OnPaint(self, event):
                if self.firstpaint:
                        if self.GetSashPosition() != self.GetExpectedSashPosition():
                                self.ResetSash()
                        self.firstpaint = False
                event.Skip()


class TestAppFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.split = ProportionalSplitter(self, wx.ID_ANY)
        self.panel1 = wx.Panel(self.split, wx.ID_ANY)
        self.panel2 = wx.Panel(self.split, wx.ID_ANY)

        self.steps_list = lv.ObjectListView(self.split, -1,
                                                    style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                                    sortable=False,
                                                    cellEditMode=lv.ObjectListView.CELLEDIT_DOUBLECLICK)

        step_cols = [lv.ColumnDefn('Operation', 'left', 120, 'title'),
                     lv.ColumnDefn('Type', 'left', 100, 'value_title')]

        self.steps_list.SetColumns(step_cols)
        # TEMP FOR DRAG TESTING
        self.steps_list.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_list_drag)

        d1 = Data(range(43), 'Up to meaning of life')
        d2 = Data(range(100), 'Centennial')
        d1.value_title = 'List of Ints'
        d2.value_title = 'List of Ints'

        states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

        d3 = Data(states, 'State Abbreviations')
        d4 = Data('I only have a single value', 'Simple string')
        d5 = Data(154, 'Constant Int')
        d3.value_title = 'List of Strings'

        self.steps_list.SetObjects([d1, d2, d3, d4, d5])

        self.test = DynamicSentence(self, self.panel2)
        self.test.add_text('Suppose that an extra ')
        self.test.add_scrubber(map(lambda x: '$' + str(x), range(51)), '$25', can_drop=True)
        self.test.add_text(' was charged to ')
        self.test.add_scrubber(map(lambda x: str(x) + '%', range(101)), '25%', can_drop=True)
        self.test.add_text(' of ')
        self.test.add_clicker(['California taxpayers', 'vehicle vegistrations'],
                               'California taxpayers')
        self.test.add_text('. Park admission would be ')

        to_add = ['free'] + map(lambda x: '$' + str(x), range(1, 26))
        self.test.add_scrubber(to_add, '$10')
        self.test.add_text(' for ')
        self.test.add_clicker(['everyone', ' those who paid the charge'], 'everyone', can_drop=True)
        self.test.add_text('.')

        self.test.change_rate = .5
        self.test.set_dyn_font(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.test.set_static_font(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        for item in self.test.dyn_text:
            print item.GetLabel()


        for item in self.test.static_text:
            print item.GetLabel()

        # Uncomment for wx inspection tool of different widgets
        # wx.lib.inspection.InspectionTool().Show()

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Testbed Framework")
        self.SetSize((800, 300))

        self.panel1.SetBackgroundColour('GRAY')
        # self.panel2.SetBackgroundColour('CYAN')

    def __do_layout(self):
        self.split.SplitVertically(self.steps_list, self.panel2)

    def on_list_drag(self, event):
        # Build a string only identifier so that the dragtarget can make sense of
        # what data is getting put into it, and look it up in a view somewhere
        dataObj = event.GetEventObject().GetSelectedObject()
        data_index = event.GetEventObject().GetIndexOf(dataObj)
        olv_id = str(event.GetEventObject().GetId())

        # Id in the form of wxID olv_index
        id_string = str(olv_id) + ' ' + str(data_index)

        #  Create a Text Data Object, which holds the text that is to be dragged
        tdo = wx.PyTextDataObject(id_string)
        #  Create a Drop Source Object, which enables the Drag operation
        tds = wx.DropSource(self)
        #  Associate the Data to be dragged with the Drop Source Object
        tds.SetData(tdo)
        #  Initiate the Drag Operation
        tds.DoDragDrop(True)


if __name__ == "__main__":
    app = wx.App(False)
    # wx.InitAllImageHandlers()
    frame_1 = TestAppFrame(None, wx.ID_ANY, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
