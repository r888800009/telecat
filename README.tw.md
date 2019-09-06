# Telecat
<p align="center">
  <img src="https://raw.githubusercontent.com/r888800009/telecat/master/img.svg?sanitize=true">
</p>
什麼是telecat? telecat可以將cli程式與telegram bot進行連結，
也就是說透過c/c++、java、ruby或其他程式語言寫成的程式，
皆可透過telecat套用在telegram bot上。

**telecat**名稱的由來是取自於**telegram**與**netcat**
兩個單詞創造出來的。

telecat有哪些潛力? 進行開發測試時不需要重新編寫bot，
將已經寫好的cli程式佈署在telegram，對於測試而言不需要
去了解telegram bot api即可生成一個可使用的telegram bot程式。

為什麼telecat會被創造出來? telecat原本打算作為pwn的交互界面，
可以透過telecat去把寫好的腳本套用在bot上，之後可以使用
telegram下去操作交互界面而不是終端機，可以telecat也可以在群組上面使用。

telegram的運作原理，是將輸入的內容傳到程式的stdin以及stdout，
並且可以對多個群組同時開啟多個程式，只須輸入`/start`即可在的群組
開啟cli程式，透過`/stop`即可關閉程式。
