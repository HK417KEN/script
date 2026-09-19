// ==UserScript==
// @name        BiliVideoCustom
// @namespace   Violentmonkey Scripts
// @icon
// @version     1.0.0
//
// @match       *://www.bilibili.com/video/BV*
// @grant       none
//
// @author      Ken
// @description Skip video login on Bilibili
// ==/UserScript==


class BiliVideoCustomSettings {
  initOnlyOnceLocalStorageId = 'bili_video_custom_settings_is_init'
  settingsKey = 'bpx_player_profile'
  settingsValue = '{"lastUnlogintrialView":0,"lastUid":0,"aiAnimationInfo":"[]","aiPromptToastInfo":"[]","media":{"quality":0,"volume":1,"nonzeroVol":1,"hideBlackGap":true,"dolbyAudio":false,"audioQuality":null,"autoplay":false,"handoff":2,"seniorTip":true,"opEd":true,"loudnessSwitch":0,"listLoop":false,"loop":false},"dmSend":{"upDm":false,"dmChecked":true},"blockList":[],"dmSetting":{"status":true,"dmSwitch":false,"aiSwitch":true,"aiLevel":3,"preventshade":false,"dmask":false,"typeScroll":true,"typeTopBottom":true,"typeColor":true,"typeSpecial":true,"opacity":0.1,"dmarea":10,"speedplus":1.6,"fontsize":0.5,"fullscreensync":true,"speedsync":false,"fontfamily":"SimHei, \'Microsoft JhengHei\'","bold":true,"fontborder":0,"seniorModeSwitch":0,"dmdensity":2},"basEditorData":{},"audioEffect":null,"boceTimes":[],"interaction":{"rookieGuide":null,"showedDialog":false},"iswide":false,"widesave":null,"subtitle":{"fade":false,"scale":true,"fontsize":1,"opacityNew":0.87,"bilingual":false,"color":"16777215","shadow":"0","position":"bottom-center"},"translation":{"showBubbleTypes":[]},"progress":{"precisionGuide":null,"pbpstate":true,"pinstate":false},"panorama":true,"ksInfo":{"ts":0,"kss":null},"householdBroadToastShowDate":null,"exp":{}}'

  timeoutId = 0
  timeoutMS = 200

  settingsTimeoutId = 0
  settingsTimeoutMS = 1000

  elInitTriggerSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-full'

  video = null

  initOnlyOnce() {
    let loopInitSetSettings = () => {
      this.timeoutId = setTimeout(() => {
        this.stopVideoAutoPlay()
        let elInitTrigger = document.querySelector(this.elInitTriggerSelector)
        if (elInitTrigger) {
          this.timeoutId = 0

          this.settingsTimeoutId = setTimeout(() => {
            localStorage.setItem(this.settingsKey, this.settingsValue)
            localStorage.setItem(this.initOnlyOnceLocalStorageId, 'true')
            location.reload()
          }, this.settingsTimeoutMS)
        } else {
          loopInitSetSettings()
        }
      }, this.timeoutMS)
    }

    let isInit = localStorage.getItem(this.initOnlyOnceLocalStorageId)
    if (isInit !== 'true') {
      this.stopVideoAutoPlay()
      localStorage.setItem(this.settingsKey, this.settingsValue)
      localStorage.setItem('recommend_auto_play', 'close')
      loopInitSetSettings()
    }
  }

  stopVideoAutoPlay() {
    if (!this.video) {
      this.video = document.querySelector('video')
    }
    this.video.pause()
    this.video.removeAttribute('preload')
  }
}


class BiliVideoSkipLogin {

  elCloseToastTargetSelector = '.bpx-player-toast-auto .bpx-player-toast-cancel'
  closeFirstVideoToastTimeoutId = 0
  closeFirstVideoToastTimeoutMS = 200

  elLoopCloseTargetSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-wide'
  elWidePlayerSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-wide'
  widePlayerOnPlayerLoadedTimeoutId = 0
  widePlayerOnPlayerLoadedTimeoutMS = 200

  elLoopCloseTriggerSelector = '.bili-mini-login-right-wp'
  elLoopCloseTargetSelector = '.bili-mini-content-wp .bili-mini-close-icon'
  elFullScreenSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-full'
  loopCloseTimeoutId = 0
  loopCloseTimeoutMS = 200

  elLoopRemoveCommentsLoginTipTriggerSelector = 'bili-comments:nth-child(1)'
  elLoopRemoveCommentsLoginTipTargetSelector = '#limit-mask'
  removeCommentsLoginTipTimeoutId = 0
  removeCommentsLoginTipTimeoutMS = 1000

  init() {
    this.loopClose()
    this.widePlayerOnPlayerLoaded()
    this.closeFirstVideoToast()
    this.removeCommentsLoginTip()
  }

  loopClose() {
    this.loopCloseTimeoutId = setTimeout(() => {
      let elLoopCloseTrigger = document.querySelector(this.elLoopCloseTriggerSelector)
      if (elLoopCloseTrigger) {
        let elTarget = document.querySelector(this.elLoopCloseTargetSelector)
        elTarget.click()
        let elFullScreen = document.querySelector(this.elFullScreenSelector)
        if (elFullScreen) {
          elFullScreen.dispatchEvent((new Event('click', {bubbles: true})))
        }
      }
      this.loopClose()
    }, this.loopCloseTimeoutMS)
  }

  widePlayerOnPlayerLoaded() {
    this.widePlayerOnPlayerLoadedTimeoutId = setTimeout(() => {
      let elWidePlayer = document.querySelector(this.elWidePlayerSelector)
      if (elWidePlayer) {
        elWidePlayer.click()
      } else {
        this.widePlayerOnPlayerLoaded()
      }
    }, this.widePlayerOnPlayerLoadedTimeoutMS)
  }

  // document.getElementsByTagName('bili-comments')[0].shadowRoot.querySelector('#limit-mask').style.setProperty('display', 'none')
  removeCommentsLoginTip() {
    document.getElementsByTagName('bili-comments')[0]
    this.removeCommentsLoginTipTimeoutId = setTimeout(() => {
      let elCloseToastTarget = document.querySelector(this.elLoopRemoveCommentsLoginTipTriggerSelector)
      if (elCloseToastTarget) {
        let elLoopRemoveCommentsLoginTipTarget = elCloseToastTarget.shadowRoot.querySelector(this.elLoopRemoveCommentsLoginTipTargetSelector)
        if (elLoopRemoveCommentsLoginTipTarget) {
          elLoopRemoveCommentsLoginTipTarget.style.setProperty('display', 'none')
        } else {
          this.removeCommentsLoginTip()
        }
      } else {
        this.removeCommentsLoginTip()
      }
    }, this.removeCommentsLoginTipTimeoutMS)
  }

  closeFirstVideoToast() {
    this.closeFirstVideoToastTimeoutId = setTimeout(() => {
      let elCloseToastTarget = document.querySelector(this.elCloseToastTargetSelector)
      if (elCloseToastTarget) {
        elCloseToastTarget.click()
      } else {
        this.closeFirstVideoToast()
      }
    }, this.closeFirstVideoToastTimeoutMS)
  }
}


class BiliVideoOneClickFullscreenAndPlay {
  elInitTriggerSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-full'
  elClickTriggerSelector = '#mirror-vdcon'
  elFullScreenSelector = '.bpx-player-ctrl-btn.bpx-player-ctrl-full'
  timeoutId = 0
  timeoutMS = 200
  loopInit() {
    this.timeoutId = setTimeout(() => {
      let elInitTrigger = document.querySelector(this.elInitTriggerSelector)
      if (elInitTrigger) {

        this.timeoutId = 0

        let elClickTrigger = document.querySelector(this.elClickTriggerSelector)
        if (elClickTrigger) {
          elClickTrigger.addEventListener('click', e => {

            if (e.target !== e.currentTarget) {
              return
            }

            let elFullScreen = document.querySelector(this.elFullScreenSelector)
            if (elFullScreen) {
              elFullScreen.dispatchEvent((new Event('click', {bubbles: true})))
            }
          })

        }
      } else {
        this.loopInit()
      }
    }, this.timeoutMS)
  }
}



window.BiliVideoCustomSettings = new BiliVideoCustomSettings
window.BiliVideoCustomSettings.initOnlyOnce()

window.BiliVideoSkipLogin = new BiliVideoSkipLogin
window.BiliVideoSkipLogin.init()

window.BiliVideoOneClickFullscreenAndPlay = new BiliVideoOneClickFullscreenAndPlay
window.BiliVideoOneClickFullscreenAndPlay.loopInit()

