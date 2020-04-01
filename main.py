# -*- coding: utf-8 -*-
import pywikibot
from pywikibot import pagegenerators
from datetime import datetime
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

def IsMarkedForDeletion(pagetext):
    LowerCasePageText = pagetext.lower()
    if (
        (LowerCasePageText.find('{{No permission since') != -1) or
        (LowerCasePageText.find('{{delete') != -1) or
        (LowerCasePageText.find('{{copyvio') != -1) or
        (LowerCasePageText.find('{{speedy') != -1)
        ):
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

def ChannelChk(ChannelId):
    PageOfTrustedChannelId = pywikibot.Page(SITE, "User:YouTubeReviewBot/Trusted")
    TextOfPageOfTrustedChannelId = PageOfTrustedChannelId.get(get_redirect=True, force=True)
    if (TextOfPageOfTrustedChannelId.find(ChannelId) != -1):
        return "Trusted"
    PageOfBadChannelId = pywikibot.Page(SITE, "User:YouTubeReviewBot/bad-authors")
    TextOfPageOfBadChannelId = PageOfBadChannelId.get(get_redirect=True, force=True)
    if (TextOfPageOfBadChannelId.find(ChannelId) != -1):
        return "Bad"
    return "Unknown"
    

def checkfiles():
    category = pywikibot.Category(SITE,'License_review_needed_(video)')
    gen = pagegenerators.CategorizedPageGenerator(category)
    for page in gen:
        filename = page.title()
        print(filename)
        page = pywikibot.Page(SITE, filename)
        pagetext = page.get(get_redirect=True)
        old_text = pagetext
        global LowerCasePageText
        LowerCasePageText = pagetext.lower()
        if IsMarkedForDeletion(pagetext) == True:continue

        elif OwnWork():
            new_text = re.sub(RegexOfLicenseReviewTemplate, "" , old_text)
            EditSummary = "@%s Removing licenseReview Template, not required for ownwork." % uploader(filename,link=True)
            try:
                commit(old_text, new_text, page, EditSummary)
            except pywikibot.LockedPage as error:
                out("Page is locked '%s'." % error, 'red')
                continue

        elif DetectSite(pagetext) == "Flickr":
            new_text = re.sub(RegexOfLicenseReviewTemplate, "{{FlickrReview}}" , old_text)
            EditSummary = "@%s Marking for flickr review, file added to [[Category:Flickr videos review needed]]." % uploader(filename,link=True)
            try:
                commit(old_text, new_text, page, EditSummary)
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
                commit(old_text, new_text, page, EditSummary)
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
            if ((
                webpage.find('YouTube account associated with this video has been terminated') or
                webpage.find('playerErrorMessageRenderer') or
                webpage.find('Video unavailable') or
                webpage.find('If the owner of this video has granted you access') or
                (webpage.find('player-unavailable') and webpage.find('Sorry about that'))
                ) != -1):
                    not_available_page_name = "User:YouTubeReviewBot/Video not available on YouTube and marked for license review/%s" % (datetime.utcnow()).strftime('%B %Y')
                    not_available_page = pywikibot.Page(SITE, not_available_page_name)
                    try:
                        not_available_old_text = not_available_page.get(get_redirect=True, force=True)
                    except pywikibot.NoPage:
                        not_available_old_text = "<gallery>\n</gallery>"
                    if (not_available_old_text.find(filename) != -1):
                        continue
                    else:pass
                    not_available_new_text = re.sub("</gallery>", "%s|Uploader Name : %s <br> video url : %s <br> oldest archive : %s \n</gallery>" % ( filename, uploader(filename,link=True), OriginalURL , oldest_archive_url) , not_available_old_text)
                    EditSummary = "Adding [[%s]] which is uploaded by %s" % (filename, uploader(filename,link=True))
                    try:
                        commit(not_available_old_text, not_available_new_text, not_available_page, EditSummary)
                    except pywikibot.LockedPage as error:
                        print(colored("Page is locked '%s'." % error, 'red'))
                        continue
            else:
                pass
            YouTubeChannelIdRegex1 = r"data-channel-external-id=\"(.{0,30})\""
            YouTubeChannelIdRegex2 = r"[\"']externalChannelId[\"']:[\"']([a-zA-Z0-9_-]{0,25})[\"']"
            YouTubeChannelNameRegex1 = r"\\\",\\\"author\\\":\\\"(.{1,50})\\\",\\\""
            YouTubeChannelNameRegex2 = r"\"ownerChannelName\\\":\\\"(.{1,50})\\\","
            YouTubeChannelNameRegex3 = r"Unsubscribe from ([^<{]*?)\?"
            YouTubeVideoTitleRegex1 = r"\"title\":\"(.{1,160})\",\"length"
            YouTubeVideoTitleRegex2 = r"<title>(?:\s*|)(.{1,250})(?:\s*|)- YouTube(?:\s*|)</title>"

            # try to get channel Id
            try:
                YouTubeChannelId = re.search(YouTubeChannelIdRegex1,webpage).group(1)
            except AttributeError:
                try:
                    YouTubeChannelId = re.search(YouTubeChannelIdRegex2,webpage).group(1)
                except AttributeError:
                    continue

            # try to get Channel name
            try:
                YouTubeChannelName  = re.search(YouTubeChannelNameRegex1,webpage).group(1)
            except AttributeError:
                try:
                    YouTubeChannelName  = re.search(YouTubeChannelNameRegex2,webpage).group(1)
                except AttributeError:
                    continue

            # try to get YouTube Video's Title
            try:
                YouTubeVideoTitle   = re.search(YouTubeVideoTitleRegex1,webpage).group(1)
            except AttributeError:
                try:
                    YouTubeVideoTitle   = re.search(YouTubeVideoTitleRegex2,webpage).group(1)
                except AttributeError:
                    continue

            # Clean shit, if present in Video title or Channel Name
            YouTubeChannelName = re.sub(r'[{}\|\+\]\[]', r'-', YouTubeChannelName)
            YouTubeVideoTitle  = re.sub(r'[{}\|\+\]\[]', r'-', YouTubeVideoTitle )
            TAGS = str(
                "{{YouTubeReview"
                "|id=" + YouTubeVideoId + 
                "|ChannelName=" + YouTubeChannelName + 
                "|ChannelID=" + YouTubeChannelId +
                "|title=" + YouTubeVideoTitle + 
                "|archive=" + archive_url +
                "|date=" + informatdate() +
                "}}"
                )

            TrustTextAppend = "[[User:YouTubeReviewBot/Trusted|✔️ - Trusted YouTube Channel of  %s ]]" %  YouTubeChannelName
            EditSummary = TrustTextAppend, "License review passed", " Title of video:", YouTubeVideoTitle, "Channel Name:", YouTubeChannelName , " Video ID:", YouTubeVideoId,  " Channel ID:", YouTubeChannelId, "Archived Video on WayBack Machine"

            if re.search(r"Creative Commons", webpage) is not None or ChannelChk(YouTubeChannelId) == "Trusted":
                new_text = re.sub(RegexOfLicenseReviewTemplate, TAGS, old_text)
            else:
                continue
            if new_text == old_text:continue
            else:pass
            try:
                commit(old_text, new_text, page, EditSummary)
            except pywikibot.LockedPage as error:
                print(colored("Page is locked '%s'." % error, 'red'))
                continue

        else:continue
            

def main():
    global SITE
    SITE = pywikibot.Site()
    checkfiles()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
