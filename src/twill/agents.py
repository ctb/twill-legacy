"""
Map of various User-Agent string shortcuts that can be used for testing.
"""

from typing import Dict

# noinspection HttpUrlsUsage
agents: Dict[str, str] = dict(
    # Desktop
    chrome_40='Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36'
              ' (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
    chrome_107='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
               ' (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    edge_12='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/42.0.2311.135'
            ' Safari/537.36 Edge/12.246',
    edge_107='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
             ' (KHTML, like Gecko) Chrome/107.0.0.0'
             ' Safari/537.36 Edg/107.0.1418.26',
    firefox_40='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)'
               ' Gecko/20100101 Firefox/40.1',
    firefox_106='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0)'
                ' Gecko/20100101 Firefox/106.0',
    ie_3='Mozilla/2.0 (compatible; MSIE 3.0; Windows 3.1)',
    ie_4='Mozilla/4.0 (compatible; MSIE 4.0; Windows NT 5.0)',
    ie_5='Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.0)',
    ie_6='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    ie_7='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    ie_8='Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    ie_9='Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    ie_10='Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    ie_11='Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    ie_mobile_9='Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5;'
                ' Trident/5.0; IEMobile/9.0)',
    opera_7='Opera/7.0 (Windows NT 5.1; U) [en]',
    opera_8='Opera/8.00 (Windows NT 5.1; U; en)',
    opera_9='Opera/9.00 (Windows NT 5.2; U; en)',
    opera_10='Opera/9.80 (Windows NT 6.1; U; en) Presto/2.2.15 Version/10.00',
    opera_11='Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.00',
    opera_12='Opera/12.0 (Windows NT 5.1; U; en)'
             ' Presto/22.9.168 Version/12.00',
    opera_mini_7='Opera/9.80 (Android; Opera Mini/7.0.29952/28.2075; en)'
                 ' Presto/2.8.119 Version/11.10',
    opera_mini_9='Opera/9.80 (J2ME/MIDP; Opera Mini/9 (Compatible; MSIE:9.0;'
                 ' iPhone; BlackBerry9700; AppleWebKit/24.746; en)'
                 ' Presto/2.5.25 Version/10.54',
    konqueror_3='Mozilla/5.0 (compatible; Konqueror/3.0; Linux)',
    konqueror_4='Mozilla/5.0 (compatible; Konqueror/4.0; Linux)'
                ' KHTML/4.0.3 (like Gecko)',
    lynx_2_8='Lynx/2.8.7rel.2 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/1.0.0a',
    w3m_0_5='w3m/0.5.2 (Linux i686; it; Debian-3.0.6-3)',
    netscape_3='Mozilla/3.0 (X11; I; AIX 2)',
    netscape_4='Mozilla/4.0 (compatible; Mozilla/5.0 ; Linux i686)',
    netscape_4_5='Mozilla/4.5 [en] (X11; I; SunOS 5.6 sun4u)',
    netscape_7='Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.0.1)'
               ' Gecko/20020921 Netscape/7.0',
    netscape_9='Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.8pre)'
               ' Gecko/20071015 Firefox/2.0.0.7 Navigator/9.0',
    palemoon_25='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:25.6)'
                ' Gecko/20150723 Firefox/31.9 PaleMoon/25.6.0',
    safari_1='Mozilla/5.0 (Macintosh; PPC Mac OS X; en)'
             ' AppleWebKit/85.7 (KHTML, like Gecko) Safari/85.6',
    safari_2='Mozilla/5.0 (Macintosh; PPC Mac OS; en)'
             ' AppleWebKit/412 (KHTML, like Gecko) Safari/412',
    safari_3='Mozilla/5.0 (Macintosh; Intel Mac OS X; en)'
             ' AppleWebKit/522.7 (KHTML, like Gecko) Version/3.0 Safari/522.7',
    safari_4='Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_6; en)'
             ' AppleWebKit/530.9+ (KHTML, like Gecko)'
             'Version/4.0 Safari/528.16',
    safari_5='Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en)'
             ' AppleWebKit/534.1+ (KHTML, like Gecko)'
             ' Version/5.0 Safari/533.16',
    safari_6='Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536'
             '.26 (KHTML, like Gecko)'
             ' Version/6.0 Mobile/10A5355d Safari/8536.25',
    safari_7='Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537'
             '.51.2 (KHTML, like Gecko)'
             ' Version/7.0 Mobile/11D257 Safari/9537.53',
    safari_605='Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0)'
               ' AppleWebKit/605.1.15 (KHTML, like Gecko)'
               ' Version/16.1 Safari/605.1.15',
    vivaldi_5='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
              ' (KHTML, like Gecko) Chrome/107.0.0.0'
              ' Safari/537.36 Vivaldi/5.4.2753.51',
    # Android phones
    galaxy_s7='Mozilla/5.0 (Linux; Android 7.0; SM-G930VC Build/NRD90M; wv)'
              ' AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0'
              ' Chrome/58.0.3029.83 Mobile Safari/537.36',
    galaxy_s10='Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011)'
               ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100'
               ' Mobile Safari/537.36',
    galaxy_s20='Mozilla/5.0 (Linux; Android 10;'
               ' SM-G980F Build/QP1A.190711.020; wv) AppleWebKit/537.36'
               ' (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.96'
               ' Mobile Safari/537.36',
    galaxy_s22='Mozilla/5.0 (Linux; Android 12;'
               ' SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36'
               ' (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119'
               ' Mobile Safari/537.36',
    google_pixel='Mozilla/5.0 (Linux; Android 7.1.1; Google Pixel'
                 ' Build/NMF26F; wv) AppleWebKit/537.36 (KHTML, like Gecko)'
                 ' Version/4.0 Chrome/54.0.2840.85 Mobile Safari/537.36',
    google_pixel4='Mozilla/5.0 (Linux; Android 10; Google Pixel 4'
                  ' Build/QD1A.190821.014.C2; wv) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108'
                  ' Mobile Safari/537.36',
    google_pixel_6='Mozilla/5.0 (Linux; Android 12; Pixel 6'
                   ' Build/SD1A.210817.023; wv) AppleWebKit/537.36'
                   ' (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71'
                   ' Mobile Safari/537.36',
    nexus_6p='Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P)'
             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83'
             ' Mobile Safari/537.36',
    sony_xperia_1='Mozilla/5.0 (Linux; Android 9;'
                  ' J8110 Build/55.0.A.0.552; wv) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99'
                  ' Mobile Safari/537.36',
    htc_one_x10='Mozilla/5.0 (Linux; Android 6.0; HTC One'
                ' X10 Build/MRA58K; wv) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98'
                ' Mobile Safari/537.36',
    # iPhones
    iphone_6='Mozilla/5.0 (Apple-iPhone7C2/1202.466; U; CPU like Mac OS X; en)'
             ' AppleWebKit/420+ (KHTML, like Gecko) Version/3.0'
             ' Mobile/1A543 Safari/419.3',
    iphone_7='Mozilla/5.0 (iPhone9,3; U; CPU iPhone OS 10_0_1 like Mac OS X)'
             ' AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0'
             ' Mobile/14A403 Safari/602.1',
    iphone_8='Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)'
             ' AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0'
             ' Mobile/15A5341f Safari/604.1',
    iphone_x='Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)'
             ' AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0'
             ' Mobile/15A372 Safari/604.1',
    iphone_11='Mozilla/5.0 (iPhone12,1; U; CPU iPhone OS 13_0 like Mac OS X)'
              ' AppleWebKit/602.1.50 (KHTML, like Gecko)'
              ' Version/10.0 Mobile/15E148 Safari/602.1',
    iphone_12='Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X)'
              ' AppleWebKit/602.1.50 (KHTML, like Gecko)'
              ' Version/10.0 Mobile/15E148 Safari/602.1',
    iphone_13_pro_max='Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0'
                      ' like Mac OS X) AppleWebKit/602.1.50'
                      ' (KHTML, like Gecko) Version/10.0'
                      ' Mobile/19A346 Safari/602.1',
    iphone_se_3='Mozilla/5.0 (iPhone14,6; U; CPU iPhone OS 15_4'
                ' like Mac OS X) AppleWebKit/602.1.50'
                ' (KHTML, like Gecko) Version/10.0 Mobile/19E241 Safari/602.1',
    # MS Windows phones
    ms_lumia_650='Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft;'
                 ' RM-1152) AppleWebKit/537.36 (KHTML, like Gecko)'
                 ' Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254',
    ms_lumia_950='Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft;'
                 ' Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko)'
                 ' Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/13.1058',
    # Tablets
    galaxy_tab_s8='Mozilla/5.0 (Linux; Android 12;'
                  ' SM-X906C Build/QP1A.190711.020; wv) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119'
                  ' Mobile Safari/537.36',
    lenovo_yoga_tab_11='Mozilla/5.0 (Linux; Android 11; Lenovo YT-J706X)'
                       ' AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Chrome/96.0.4664.45 Safari/537.36',
    sony_xperia_tab_z4='Mozilla/5.0 (Linux; Android 6.0.1;'
                       ' SGP771 Build/32.2.A.0.253; wv) AppleWebKit/537.36'
                       ' (KHTML, like Gecko) Version/4.0'
                       ' Chrome/52.0.2743.98 Safari/537.36',
    galaxy_tab_s3='Mozilla/5.0 (Linux; Android 7.0; SM-T827R4 Build/NRD90M)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/60.0.3112.116 Safari/537.36',
    amazon_fire_hdx_7='Mozilla/5.0 (Linux; Android 4.4.3; KFTHWI Build/KTU84M)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Silk/47.1.79'
                      ' like Chrome/47.0.2526.80 Safari/537.36',
    lg_g_pad_7='Mozilla/5.0 (Linux; Android 5.0.2; LG-V410/V41020c'
               ' Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko)'
               ' Version/4.0 Chrome/34.0.1847.118 Safari/537.36',
    # E-Readers
    kindle_4='Mozilla/5.0 (X11; U; Linux armv7l like Android; en-us)'
             ' AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0'
             ' Safari/533.2+ Kindle/3.0+',
    kindle_3='Mozilla/5.0 (Linux; U; en-US) AppleWebKit/528.5+'
             ' (KHTML, like Gecko, Safari/528.5+) Version/4.0 Kindle/3.0'
             ' (screen 600x800; rotate)',
    # Set tops
    chromecast='Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36'
               ' (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
    amazon_4k_fire_tv='Mozilla/5.0 (Linux; Android 5.1; AFTS Build/LMY47O)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0'
                      ' Chrome/41.99900.2250.0242 Safari/537.36',
    nexus_player='Dalvik/2.1.0 (Linux; U; Android 6.0.1;'
                 ' Nexus Player Build/MMB29T)',
    apple_tv_6='AppleTV11,1/11.1',
    apple_tv_5='AppleTV6,2/11.1',
    apple_tv_4='AppleTV5,3/9.1.1',
    # Game consoles
    playstation_5='Mozilla/5.0 (PlayStation; PlayStation 5/2.26)'
                  ' AppleWebKit/605.1.15 (KHTML, like Gecko)'
                  ' Version/13.0 Safari/605.1.15',
    playstation_4='Mozilla/5.0 (PlayStation 4 3.11) AppleWebKit/537.73'
                  ' (KHTML, like Gecko)',
    xbox_x='Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X)'
           ' AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/48.0.2564.82 Safari/537.36 Edge/20.02',
    xbox_one='Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Xbox; Xbox One)'
             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0'
             ' Mobile Safari/537.36 Edge/13.10586',
    nintendo_switch='Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet)'
                    ' AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.5.10'
                    ' NintendoBrowser/5.1.0.13343',
    # Bots
    google_bot_2='Mozilla/5.0 (compatible; Googlebot/2.1;'
                 ' +http://www.google.com/bot.html)',
    bing_bot_2='Mozilla/5.0 (compatible; bingbot/2.0;'
               ' +http://www.bing.com/bingbot.htm)',
    yahoo_bot='Mozilla/5.0 (compatible; Yahoo! Slurp;'
              ' http://help.yahoo.com/help/us/ysearch/slurp)',
)
