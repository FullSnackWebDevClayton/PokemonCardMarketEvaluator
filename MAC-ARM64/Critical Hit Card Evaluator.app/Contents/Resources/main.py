import wx
import wx.adv
import requests
import re

class eBayScraper(wx.Frame):
    def __init__(self, parent, title):
        super(eBayScraper, self).__init__(parent, title=title, size=(1000, 1000))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.name_instruction = wx.StaticText(panel, label="You only need to type 'charizard' or if you need the grading company to be ACE for example then put 'charizard ace'.")
        font = self.name_instruction.GetFont()
        font.SetPointSize(9)
        self.name_instruction.SetFont(font)
        vbox.Add(self.name_instruction, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.search_label = wx.StaticText(panel, label="Card Name:")
        self.search_field = wx.TextCtrl(panel)
        hbox1.Add(self.search_label, flag=wx.RIGHT, border=15)
        hbox1.Add(self.search_field, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.cardnum_instruction = wx.StaticText(panel, label="Enter the card number exactly as it appears, including variations (e.g., '25/100').")
        font = self.cardnum_instruction.GetFont()
        font.SetPointSize(9)
        self.cardnum_instruction.SetFont(font)
        vbox.Add(self.cardnum_instruction, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.cardnum_label = wx.StaticText(panel, label="Card Number:")
        self.cardnum_field = wx.TextCtrl(panel)
        hbox2.Add(self.cardnum_label, flag=wx.RIGHT, border=15)
        hbox2.Add(self.cardnum_field, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)
        
        hbox_grade = wx.BoxSizer(wx.HORIZONTAL)
        self.grade_label = wx.StaticText(panel, label="Grade / Ungraded:")
        self.grade_choice = wx.Choice(panel, choices=["Ungraded"] + [str(x) for x in range(1, 11)] + ["9.5"])
        self.grade_choice.SetSelection(0)
        hbox_grade.Add(self.grade_label, flag=wx.RIGHT, border=15)
        hbox_grade.Add(self.grade_choice, proportion=1)
        vbox.Add(hbox_grade, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.holo_checkbox = wx.CheckBox(panel, label="Exclude Holo")
        vbox.Add(self.holo_checkbox, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.reverse_holo_checkbox = wx.CheckBox(panel, label="Exclude Reverse Holo")
        vbox.Add(self.reverse_holo_checkbox, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.japanese_checkbox = wx.CheckBox(panel, label="Exclude Japanese")
        vbox.Add(self.japanese_checkbox, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.english_checkbox = wx.CheckBox(panel, label="Exclude English")
        vbox.Add(self.english_checkbox, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.location_instruction = wx.StaticText(panel, label="Warning, UK vendors will not payout at worldwide price due to USA market.")
        font = self.location_instruction.GetFont()
        font.SetPointSize(9)
        self.location_instruction.SetFont(font)
        vbox.Add(self.location_instruction, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.location_label = wx.StaticText(panel, label="Location:")
        self.location_uk = wx.RadioButton(panel, label="UK", style=wx.RB_GROUP)
        self.location_uk.SetValue(True)
        self.location_worldwide = wx.RadioButton(panel, label="Worldwide")
        hbox3.Add(self.location_label, flag=wx.RIGHT, border=15)
        hbox3.Add(self.location_uk)
        hbox3.Add(self.location_worldwide, flag=wx.LEFT, border=15)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.vendor_instruction = wx.StaticText(panel, label="Leave this at 100 if you don't want to check vendor payout.")
        font = self.vendor_instruction.GetFont()
        font.SetPointSize(9)
        self.vendor_instruction.SetFont(font)
        vbox.Add(self.vendor_instruction, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        hbox_payout = wx.BoxSizer(wx.HORIZONTAL)
        self.payout_label = wx.StaticText(panel, label="Vendor Payout Percentage (%):")
        self.payout_input = wx.TextCtrl(panel)
        self.payout_input.SetValue("100")
        hbox_payout.Add(self.payout_label, flag=wx.RIGHT, border=8)
        hbox_payout.Add(self.payout_input, proportion=1)
        vbox.Add(hbox_payout, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        hbox_results_range = wx.BoxSizer(wx.HORIZONTAL)
        self.results_range_label = wx.StaticText(panel, label="Results Limit:")
        self.results_60 = wx.RadioButton(panel, label="Last 60 Sold", style=wx.RB_GROUP)
        self.results_120 = wx.RadioButton(panel, label="Last 120 Sold")
        self.results_240 = wx.RadioButton(panel, label="Last 240 Sold")
        self.results_60.SetValue(True)
        hbox_results_range.Add(self.results_range_label, flag=wx.RIGHT, border=15)
        hbox_results_range.Add(self.results_60, flag=wx.RIGHT, border=10)
        hbox_results_range.Add(self.results_120, flag=wx.RIGHT, border=10)
        hbox_results_range.Add(self.results_240, flag=wx.RIGHT, border=10)
        vbox.Add(hbox_results_range, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.search_btn = wx.Button(panel, label="Search")
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        vbox.Add(self.search_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=15)

        self.price_label = wx.StaticText(panel, label="Lowest Price: £--.-- | Average Price: £--.-- | Highest Price: £--.--")
        vbox.Add(self.price_label, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.payout_display = wx.StaticText(panel, label="Vendor Payout: £--.--")
        vbox.Add(self.payout_display, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.result_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.result_list.InsertColumn(0, "Title", width=550)
        self.result_list.InsertColumn(1, "Price", width=80)
        self.result_list.InsertColumn(2, "Sold Date", width=100)
        vbox.Add(self.result_list, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        hbox_discord = wx.BoxSizer(wx.HORIZONTAL)
        self.discord_link = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="Critical Hit Collectables Discord", url="https://discord.gg/jdXCEwMDrk")
        hbox_discord.Add(self.discord_link, proportion=1, flag=wx.LEFT, border=8)
        vbox.Add(hbox_discord, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)

        hbox_donation = wx.BoxSizer(wx.HORIZONTAL)
        self.donation_label = wx.StaticText(panel, label="PayPal Donations Email:")
        self.donation_email = wx.TextCtrl(panel, value="support@criticalhitcollectables.co.uk", style=wx.TE_READONLY)
        self.copy_btn = wx.Button(panel, label="Copy")
        self.copy_btn.Bind(wx.EVT_BUTTON, self.on_copy_email)
        hbox_donation.Add(self.donation_label, flag=wx.RIGHT, border=8)
        hbox_donation.Add(self.donation_email, proportion=1, flag=wx.RIGHT, border=8)
        hbox_donation.Add(self.copy_btn, flag=wx.LEFT, border=10)
        vbox.Add(hbox_donation, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def on_copy_email(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.donation_email.GetValue()))
            wx.TheClipboard.Close()
            wx.MessageBox("Email address copied to clipboard!", "Info", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error", wx.OK | wx.ICON_ERROR)

    def on_search(self, event):
        search_term = self.search_field.GetValue().strip()
        card_number = self.cardnum_field.GetValue().strip()
        grade = self.grade_choice.GetStringSelection()
        location = "1" if self.location_uk.GetValue() else "2"
        results_limit = 60 if self.results_60.GetValue() else 120 if self.results_120.GetValue() else 240
        exclude_options = {
            'excludeHolo': self.holo_checkbox.IsChecked(),
            'excludeReverseHolo': self.reverse_holo_checkbox.IsChecked(),
            'excludeEnglish': self.english_checkbox.IsChecked(),
            'excludeJapanese': self.japanese_checkbox.IsChecked()
        }

        data = {
            'search_term': search_term,
            'card_number': card_number,
            'grade': grade,
            'location': location,
            'exclude_options': exclude_options,
            'results_limit': results_limit
        }
        response = requests.post('http://57.128.171.188:5176/search', json=data)
        if response.status_code == 200:
            results = response.json()
            self.update_results(results)
        else:
            wx.MessageBox("Failed to retrieve data from server.", "Error", wx.OK | wx.ICON_ERROR)

    def update_results(self, results):
        self.result_list.DeleteAllItems()
        # Adjusting the line that extracts and converts prices:
        # Strip out the currency symbol and other non-numeric characters before converting to float.
        prices = [float(re.sub(r'[^\d.]', '', result['price'])) for result in results if 'price' in result]

        if prices:
            lowest_price = min(prices)
            highest_price = max(prices)
            average_price = sum(prices) / len(prices)
            payout_percentage = float(self.payout_input.GetValue()) / 100
            vendor_payout = average_price * payout_percentage

            self.price_label.SetLabel(f"Lowest Price: £{lowest_price:.2f} | Average Price: £{average_price:.2f} | Highest Price: £{highest_price:.2f}")
            self.payout_display.SetLabel(f"Vendor Payout: £{vendor_payout:.2f}")
        else:
            self.price_label.SetLabel("Lowest Price: £--.-- | Average Price: £--.-- | Highest Price: £--.--")
            self.payout_display.SetLabel("Vendor Payout: £--.--")

        for result in results:
            index = self.result_list.InsertItem(self.result_list.GetItemCount(), result['title'])
            self.result_list.SetItem(index, 1, result['price'])
            self.result_list.SetItem(index, 2, result['soldDate'])


if __name__ == "__main__":
    app = wx.App(False)
    frame = eBayScraper(None, "Critical Hit Collectables - eBay Market Evaluation Tool")
    app.MainLoop()
