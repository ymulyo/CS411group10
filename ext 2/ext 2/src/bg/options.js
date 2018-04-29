var username = localStorage['username'] || "";
var password = localStorage['password'] || "";
document.getElementById('appliedat_username').value = username;
document.getElementById('appliedat_password').value = password;
document.getElementById('btnSaveLogin').onclick = function () {
  localStorage['username'] = document.getElementById('appliedat_username').value;
  localStorage['password'] = document.getElementById('appliedat_password').value;
  document.querySelector('#jobfinder-wrapper #saved_info').style.display = 'block';
  setTimeout(function () {
    location.reload();
  }, 10000);
};
