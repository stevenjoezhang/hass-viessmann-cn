# Viessmann CN for Home Assistant

[![通过HACS添加集成](https://my.home-assistant.io/badges/hacs_repository.svg)][hacs]

![](https://forthebadge.com/images/badges/made-with-python.svg)
![](https://forthebadge.com/images/badges/powered-by-electricity.svg)
![](https://forthebadge.com/images/badges/makes-people-smile.svg)

* 本插件支持将菲斯曼（Viessmann）中国区智能壁炉设备自动接入 [Home Assistant](https://www.home-assistant.io)
* 支持 Home Assistant 后台界面集成，无需编写 yaml 配置文件
* 能够控制暖气温度、热水温度、运行模式等
* 能够自动更新设备的在线状态、故障状态和燃烧状态
* 支持显示详细的设备信息和传感器数据

## 添加设备

首先在手机上下载「菲斯曼互联」App，并按照提示将家中的壁炉设备接入网络。

添加设备后，您可以在 App 中确认设备已在线并能正常控制。本插件能够自动读取相关信息并显示在 Home Assistant 中。

## 安装插件

在将所有设备添加完成后，将本插件安装到 Home Assistant。

### 通过 HACS 安装

如果您使用 HACS，可以直接点击[安装链接][hacs]，然后按照提示操作即可。

### 手动安装

如果不使用 HACS，可以手动安装插件。具体方法是，先克隆这个仓库到部署 Home Assistant 的主机上：

```sh
git clone https://github.com/stevenjoezhang/hass-viessmann-cn
```

然后，将其中的`custom_components/viessmann_cn`子目录复制进 Home Assistant 的数据目录。例如，数据目录是`~/hass`，那么执行以下命令：

```sh
cp -r hass-viessmann-cn/custom_components/viessmann_cn ~/hass/custom_components
```

## 配置方式

安装完成后，重启 Home Assistant。待 Home Assistant 启动后，在「设置」菜单中点击「设备与服务」选项，在新界面中选择「添加集成」，搜索「Viessmann CN」，按照提示输入您的菲斯曼账号（手机号）和密码即可。

## 功能说明

本插件目前支持以下功能：

### 暖气控制 (Climate)

* **暖气控制**：支持调节暖气目标温度。
* **模式切换**：支持切换「制热」（Heating+DHW）和「关」（仅DHW/防冻）模式。
* **状态显示**：显示当前暖气出水温度，以及壁炉是否正在燃烧（Heating 状态）。

### 热水器 (Water Heater)

* **热水控制**：支持调节生活热水目标温度。
* **状态显示**：显示当前热水出水温度。

### 传感器 (Sensor)

* **状态监测**：显示设备运行状态、故障代码、燃烧状态等详细信息。

## 隐私

本插件可能会收集您所使用的设备的`physicsId`等信息用于设备通信。这些信息仅用于插件与菲斯曼服务器交互，不会发送给第三方。

## 免责声明

请注意，对 Home Assistant 或本插件的使用可能带来安全风险。例如，通过 Home Assistant 自动化定时启动、关闭加热设备，可能因软硬件故障导致意外情况。

本插件仅供研究学习使用。请您注意用电和用气安全，本插件作者不对由使用该插件产生的任何后果负责。

[hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=stevenjoezhang&repository=hass-viessmann-cn&category=integration
