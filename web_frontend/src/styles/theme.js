// src/styles/theme.js

export const themes = {
    light: {
      colors: {
        background: {
          base: "#fef6f0",           // 页面背景
          secondary: "#fef6f0",      // 用于 border、hover 等浅色元素
          cardHome: "#ffffffcc",     // 首页卡片背景（轻透白）
          cardNav: "#fef6f0"          // 导航栏卡片背景（更偏米白）
        },
        primary: "#ffb347",           // 主按钮色
        primaryHover: "#ffa033",      // 按钮 hover 色
        text: {
          main: "#444",               // 主文字色（深灰）
          subtle: "#666"              // 副文字色（中灰）
        }
      },
      radius: {
        button: "10px"                // 所有圆角统一
      },
      shadow: {
        cardHome: "0 10px 30px rgba(0,0,0,0.08)",
        cardNav: "none"
      }
    },
  
    dark: {
      colors: {
        background: {
          base: "#2c2c2c",
          secondary: "#2c2c2c",
          cardHome: "#3a3a3a",        // 深色卡片
          cardNav: "#2c2c2c"          // 深色导航卡片
        },
        primary: "#444444",           // 暗色主按钮色
        primaryHover: "#555555",
        text: {
          main: "#f1f1f1",             // 主文字色
          subtle: "#999999"            // 副文字色
        }
      },
      radius: {
        button: "10px"
      },
      shadow: {
        cardHome: "0 10px 30px rgba(0,0,0,0.3)",
        cardNav: "none"
      }
    }
  };