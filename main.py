from selenium import webdriver
import sched, time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

s = sched.scheduler(time.time, time.sleep)

cred = credentials.Certificate('./rums.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rums-15e5f.firebaseio.com/'
})

ref = db.reference('gaana/current_playing')
history_ref = db.reference('gaana/history')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=./data")
chrome_capabilities = webdriver.DesiredCapabilities.CHROME
# chrome_capabilities['loggingPrefs'] = {'performance': 'ALL'}

driver = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=chrome_capabilities)
driver.get("https://gaana.com/playlist/satyajitghana-yyhwn-casualall")

time.sleep(10)

# for entry in driver.get_log('performance'):
#     print(entry)

script = """
var body = document.getElementsByTagName("body")[0];
var innerElements = body.children;
var toExclude = {
    "tagName": ["SCRIPT"],
	"class": [],
	"id": ["outercontainer", "video", "mp"]
};

for (var i = 0 ; i < innerElements.length ; i++) {
    if (    !toExclude.class.includes(innerElements[i].className)
        &&  !toExclude.id.includes(innerElements[i].id)
        &&  !toExclude.tagName.includes(innerElements[i].tagName)) {
        //if (innerElements[i].firstElementChild.id != null) {
        //    if (innerElements[i].firstElementChild.id=="stylesheet1")
        //        break;
        //}
        //innerElements[i].parentNode.removeChild(innerElements[i]);
        innerElements[i].remove()
        i--;
    }
}

var div = document.createElement('div');
div.innerHTML = `<link id="stylesheet1" rel="stylesheet" type="text/css" href="https://css375.gaanacdn.com/min/?b=css&amp;f=web/css/plugins-css.css,web/css/player-web.css,web/css/bg_and_sprite_load.css,web/css/bg_and_sprite_load_white.css,web/css/font_embed-web.css,web/css/media-queries.css&amp;version=963.34&amp;963.34">`;
body.appendChild(div);

/* aeee c, don't use parentElement.removeChild, 
just use .remove() of element instead, much easier.*/
/* and why not use a list for storing the ids and class
name, less lines of code, better readable*/
/* ab itna saaara khacra comment karna pad raha hai */
/*ad = document.getElementsByClassName('ads-section')[0];
ad.parentElement.removeChild(ad);
ad = document.getElementById('Gaana-Home-Top_Ads');
ad.parentElement.removeChild(ad);
ad = document.getElementById('ad_unit');
ad.parentElement.removeChild(ad);
ad = document.getElementsByClassName('adunit');
while (ad.length > 0) {
    ad[0].parentNode.removeChild(ad[0]);
}*/
document.getElementsByClassName('ads-section')[0].remove();
document.getElementById('Gaana-Home-Top_Ads').remove();
document.getElementById('ad_unit').remove();
document.getElementById('bottomPlayerAds').remove();
document.getElementById('queueAds').remove();
ad = document.getElementsByClassName('adunit');
while (ad.length > 0) {
    ad[0].remove();
}
"""

# driver.execute_script(script)


def save_current_playing():
    title = driver.find_element_by_id('stitle').text
    atitle = driver.find_element_by_id('atitle').text
    thumbnail = driver.find_element_by_xpath('//*[@id="mp"]/div[2]/div/div[1]/div[1]/a/img').get_attribute('src')
    data = {
        'title': title,
        'atitle': atitle,
        'thumbnail': thumbnail,
        'timestamp': time.time()
    }
    ref.set(data)
    history_ref.push(data)
    print(title, atitle, thumbnail)
    s.enter(10, 1, save_current_playing, ())


s.enter(10, 1, save_current_playing, ())
s.run()
