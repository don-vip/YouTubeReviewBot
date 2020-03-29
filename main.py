# -*- coding: utf-8 -*-
import pywikibot
from pywikibot import pagegenerators
from datetime import datetime
import chkdel
import savepagenow
import re
from urllib.request import Request, urlopen
RegexOfLicenseReviewTemplate = r"{{(?:|\s*)[LlYy][IiOo][CcUu][EeTt][NnUu][SsBb][Ee](?:|\s*)[Rr][Ee][Vv][Ii][Ee][Ww](?:|\s*)(?:\|.*|)}}"
def informatdate():
    return (datetime.utcnow()).strftime('%Y-%m-%d')

def commit(old_text, new_text, page, summary):
    """Show diff and submit text to page."""
    out("\nAbout to make changes at : '%s'" % page.title())
    pywikibot.showDiff(old_text, new_text)
    #page.put(new_text, summary=summary, watchArticle=True, minorEdit=False)

def out(text, newline=True, date=False, color=None):
    """Just output some text to the consoloe or log."""
    if color:
        text = "\03{%s}%s\03{default}" % (color, text)
    dstr = (
        "%s: " % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if date
        else ""
    )
    pywikibot.stdout("%s%s" % (dstr, text), newline=newline)

def isOwnWork(pagetext):
    if (LowerCasePageText.find('{{own}}') != -1):
        return True
    elif (LowerCasePageText.find('own work') != -1):
        return True

def uploader(filename, link=True):
    """user that uploaded the video"""
    page = pywikibot.Page(SITE, filename)
    history = page.getVersionHistory(reverse=True, total=1)
    if not history:
        return "Unknown"
    if link:
        return "[[User:%s|%s]]" % (history[0][2], history[0][2])
    else:
        return history[0][2]

def DetectSite(pagetext):
    if (LowerCasePageText.find('{{from vimeo') != -1):
        return "Vimeo"
    if (LowerCasePageText.find('{{from youtube') != -1):
        return "YouTube"
    elif (LowerCasePageText.find('flickr.com/photos') != -1):
        return "Flickr"
    elif (LowerCasePageText.find('vimeo.com') != -1):
        return "Vimeo"
    elif (LowerCasePageText.find('youtube.com') != -1):
        return "YouTube"

def archived_url(url):
    status = "Wait"
    while status == "Wait":
        archive_url = savepagenow.capture(url)
        try:
            archive_url
            status = "Done"
        except:
            pass
    return archive_url

def archived_webpage(archive_url):
    status = "Wait"
    while status == "Wait":
        req = Request(archive_url,headers={'User-Agent': 'User:YouTubeReviewBot on wikimedia commons'})
        try:
            webpage = urlopen(req).read().decode('utf-8')
            status = "Done"
        except:
            pass
    return webpage

def check_channel(ChannelId):
    if ChannelId in (pywikibot.Page(SITE, "User:YouTubeReviewBot/Trusted")).get(get_redirect=True, force=True):
        return "Trusted"
    elif ChannelId in (pywikibot.Page(SITE, "User:YouTubeReviewBot/bad-authors")).get(get_redirect=True, force=True):
        return "Bad"
    else:
        return "Normal"

def OwnWork():
    if (LowerCasePageText.find('{{own}}') != -1):
        return True
    elif (LowerCasePageText.find('own work') != -1):
        return True
    else:
        return False

def checkfiles():
    category = pywikibot.Category(SITE,'Animated videos uploaded by Eatcha')
    gen = pagegenerators.CategorizedPageGenerator(category)
    for page in gen:
        filename = page.title()
        print(filename)
        page = pywikibot.Page(SITE, filename)
        pagetext = page.get(get_redirect=True)
        old_text = pagetext
        global LowerCasePageText
        LowerCasePageText = pagetext.lower()
        if chkdel.check(pagetext) == True:continue # Do not review files marked for deletion

        elif OwnWork():
            new_text = re.sub(RegexOfLicenseReviewTemplate, "" , old_text)
            EditSummary = "@%s Removing licenseReview Template, not required for ownwork." % uploader(filename,link=True)
            try:
                commit(old_text, new_text, page, "{0}".format(EditSummary))
            except pywikibot.LockedPage as error:
                out("Page is locked '%s'." % error, 'red')
                continue

        elif DetectSite(pagetext) == "Flickr":
            new_text = re.sub(RegexOfLicenseReviewTemplate, "{{FlickrReview}}" , old_text)
            EditSummary = "@%s Marking for flickr review, file added to [[Category:Flickr videos review needed]]." % uploader(filename,link=True)
            try:
                commit(old_text, new_text, page, "{0}".format(EditSummary))
            except pywikibot.LockedPage as error:
                out("Page is locked '%s'." % error, 'red')
                continue

        elif DetectSite(pagetext) == "Vimeo":
            VimeoUrlPattern = re.compile(r'vimeo\.com\/((?:[0-9_]+))')
            FromVimeoRegex = re.compile(r'{{\s*?[Ff]rom\s[Vv]imeo\s*(?:\||\|1\=|\s*?)(?:\s*)(?:1\=|)(?:\s*?|)([0-9_]+)')
            try:
                VimeoVideoId = re.search(r"{{\s*?[Ff]rom\s[Vv]imeo\s*(?:\||\|1\=|\s*?)(?:\s*)(?:1\=|)(?:\s*?|)([0-9_]+)",pagetext).group(1)
            except AttributeError:
                try:
                    VimeoVideoId = re.search(r"vimeo\.com\/((?:[0-9_]+))",pagetext).group(1)
                except:
                    continue
            SourceURL = "https://vimeo.com/%s" % VimeoVideoId
            archive_url = archived_url(SourceURL)
            webpage = archived_webpage(archive_url)
            matches = re.finditer(r"http(?:s|)\:\/\/vimeo\.com\/(.{0,30})\/video", webpage, re.MULTILINE)
            for m in matches:
                VimeoChannelId = m.group(1)
            try:
                VimeoChannelId
            except:
                continue
            if check_channel(VimeoChannelId) == "Trusted":pass
            if check_channel(VimeoChannelId) == "Bad":continue
            StandardCreativeCommonsUrlRegex = re.compile('https\:\/\/creativecommons\.org\/licenses\/(.*?)\/(.*?)\/')
            Allowedlicenses = ['by-sa', 'by', 'publicdomain', 'cc0']
            if re.search(r"creativecommons.org", webpage):
                matches = StandardCreativeCommonsUrlRegex.finditer(webpage)
                for m in matches:
                    licensesP1, licensesP2  = (m.group(1)), (m.group(2))
                if licensesP1 not in Allowedlicenses:
                    continue
                else:pass
            else:
                continue
            new_text = re.sub(RegexOfLicenseReviewTemplate, "{{VimeoReview|id=%s|license=%s-%s|ChannelID=%s|archive=%s|date=%s}}" % (
                VimeoVideoId,
                licensesP1,
                licensesP2,
                VimeoChannelId,
                archive_url,
                informatdate()),
                old_text)
            EditSummary = "License review passed ", " Channel Name/ID:", VimeoChannelId, " Video ID:", VimeoVideoId, " License :", licensesP1,"-",licensesP2, "Archived Video on WayBack Machine"
            try:
                commit(old_text, new_text, page, "{0}".format(EditSummary))
            except pywikibot.LockedPage as error:
                continue

        elif DetectSite(pagetext) == "YouTube":
            try:
                YouTubeVideoId = re.search(r"{{\s*?[Ff]rom\s[Yy]ou[Tt]ube\s*(?:\||\|1\=|\s*?)(?:\s*)(?:1|=\||)(?:=|)([^\"&?\/ ]{11})",pagetext).group(1)
            except AttributeError:
                try:
                    YouTubeVideoId = re.search(r"https?\:\/\/(?:www|m|)(?:|\.)youtube\.com/watch\Wv\=([^\"&?\/ ]{11})",pagetext).group(1)
                except:
                    continue
            SourceURL = "https://www.youtube.com/watch?v=%s" % YouTubeVideoId
            archive_url = archived_url(SourceURL)
            webpage = archived_webpage(archive_url)

        else:return
            

def main():
    global SITE
    SITE = pywikibot.Site()
    checkfiles()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
