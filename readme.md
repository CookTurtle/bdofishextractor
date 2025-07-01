
# 黑色沙漠海域選擇器

本專案是以[Flockenberger/bdo-fish-waypoints](https://github.com/Flockenberger/bdo-fish-waypoints)為基底製作的自動化複製檔案程式。
原本需要在使用者id資料夾中編輯長長的gamevariable.xml檔案才能在遊戲中查看標點，現在只要動動滑鼠選取資料夾後就可以輕鬆完成!

## 🖥️ 功能特色

- 讓使用者透過模糊搜尋選擇海域並自動更改本地遊戲快取
- 自動記憶使用者資料夾設定
- 簡潔的 GUI 操作介面（PyQt5 製作）

# 📦 下載

> 最新版本：[Releases 頁面](https://github.com/CookTurtle/bdofishextractor/releases)

# 🚀 如何使用
1. 取得資料(詳見下方取得資料)
2. 下載並執行 `fishgui.exe`
3. 找到你的角色id資料夾(詳見下方尋找角色ID)
4. 關閉遊戲主程式
5. 點選「套用海域到gamevariable.xml」，即可完成操作

# ❓ 如何取得資料
1. 訪問資料作者頁面[Flockenberger/bdo-fish-waypoints](https://github.com/Flockenberger/bdo-fish-waypoints)
2. 點選旁邊的`Releases`
3. 下載`BDO-Fishing-Waypoints.zip`
4. 將壓縮檔解壓縮，並且將`BDO-Fishing-Waypoints`資料夾重新命名成`data`
5. 將`data`資料夾放置在與fishgui.exe同一個目錄下

# ❓ 如何取得角色ID
1. 訪問電腦的`文件`資料夾，如果你不知道你的文件資料夾在哪的話，在你的檔案管理員的路徑列輸入`%USERPROFILE%\Documents`
2. 接著進入資料夾`Black Desert\UserCache`
3. 如果你只有在你的電腦登過一個帳號，那扣除1和-1資料夾基本上數字比較少的那個就是你的帳號ID，不是中文家門名稱，打開後裡面會有gamevariable.xml這個檔案，基本上就可以確定這是你的帳號ID，如果你有登過別人的帳號，甚至很多人的帳號已經分不清楚誰是誰了，請繼續往下看
4. 在你右上角的放大鏡圖案中選擇`我的最愛`分頁，並且隨便儲存地圖上隨便一個點，接著關閉遊戲
5. 到上面的UserCache中把數字短的資料夾每個都看一遍，看裡面的gamevariable.xml修改時間，如果修改時間和你關遊戲的時間符合，那就代表這串數字是你的ID

## ⚠️ 免則聲明
使用這些文件、程式可能導致違反服務條款或遊戲帳戶遭受處罰，本人概不負責。請自行決定是否使用。
