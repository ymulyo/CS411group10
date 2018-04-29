// if you checked "fancy-settings" in extensionizr.com, uncomment this lines

// var settings = new Store("settings", {
//     "sample_setting": "This is how you use Store.js to remember values"
// });


//example of using a message handler from the inject scripts
if (!localStorage['first_run']) {
  localStorage['first_run'] = true;
  chrome.tabs.create({
    url : chrome.extension.getURL('options.html')
  });
}
if (!localStorage['username'])
  localStorage['username'] = '';
if (!localStorage['password'])
  localStorage['password'] = '';

chrome.extension.onMessage.addListener(
  function(request, sender, sendResponse) {
  	chrome.pageAction.show(sender.tab.id);
    sendResponse();
  });