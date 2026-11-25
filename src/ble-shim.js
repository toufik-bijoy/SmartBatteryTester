// Makes the page's existing Web Bluetooth code work inside the native Android app
// by routing it to the phone's own Bluetooth (no internet needed).
// In a normal browser (Chrome etc.) this file does nothing.
import { BleClient } from '@capacitor-community/bluetooth-le';
import { Capacitor } from '@capacitor/core';

(function () {
  if (!Capacitor.isNativePlatform()) return;

  class Emitter {
    constructor() { this._l = {}; }
    addEventListener(t, f) { (this._l[t] = this._l[t] || []).push(f); }
    removeEventListener(t, f) { if (this._l[t]) this._l[t] = this._l[t].filter(function (x) { return x !== f; }); }
    _emit(t) {
      var self = this, ev = { type: t, target: this };
      (this._l[t] || []).slice().forEach(function (f) { try { f.call(self, ev); } catch (e) { console.error(e); } });
    }
  }

  function toDV(v) {
    if (v instanceof DataView) return v;
    if (ArrayBuffer.isView(v)) return new DataView(v.buffer, v.byteOffset, v.byteLength);
    return new DataView(v);
  }

  class Characteristic extends Emitter {
    constructor(dev, service, uuid) { super(); this._d = dev; this._s = service; this.uuid = uuid; this.value = null; }
    startNotifications() {
      var self = this;
      return BleClient.startNotifications(this._d.id, this._s, this.uuid, function (dv) {
        self.value = dv; self._emit("characteristicvaluechanged");
      }).then(function () { return self; });
    }
    stopNotifications() { var self = this; return BleClient.stopNotifications(this._d.id, this._s, this.uuid).then(function () { return self; }); }
    writeValue(v) {
      var a = [this._d.id, this._s, this.uuid, toDV(v)];
      return BleClient.write.apply(BleClient, a).catch(function () { return BleClient.writeWithoutResponse.apply(BleClient, a); });
    }
  }

  class Service {
    constructor(dev, uuid) { this._d = dev; this.uuid = uuid; }
    getCharacteristic(uuid) { return Promise.resolve(new Characteristic(this._d, this.uuid, uuid)); }
  }

  class Gatt {
    constructor(dev) { this.device = dev; this.connected = false; this._gone = false; }
    connect() {
      var self = this; this._gone = false;
      return BleClient.connect(this.device.id, function () { self._lost(); }, { timeout: 15000 })
        .then(function () { self.connected = true; return self; });
    }
    _lost() { this.connected = false; if (!this._gone) { this._gone = true; this.device._emit("gattserverdisconnected"); } }
    disconnect() { var self = this; return BleClient.disconnect(this.device.id).catch(function () {}).then(function () { self._lost(); }); }
    getPrimaryService(uuid) {
      var self = this;
      return BleClient.getServices(this.device.id).then(function (list) {
        if (!list.some(function (s) { return String(s.uuid).toLowerCase() === uuid.toLowerCase(); }))
          throw new Error("Service " + uuid + " not found on this device");
        return new Service(self.device, uuid);
      });
    }
  }

  class Device extends Emitter {
    constructor(id, name) { super(); this.id = id; this.name = name; this.gatt = new Gatt(this); }
  }

  var ready = null;
  function init() {
    if (!ready) {
      ready = BleClient.initialize({ androidNeverForLocation: true })
        .then(function () { return BleClient.isEnabled(); })
        .then(function (on) { if (!on) return BleClient.requestEnable(); })
        .catch(function (e) { ready = null; throw e; });
    }
    return ready;
  }

  var shim = {
    requestDevice: function (opts) {
      opts = opts || {};
      var f = (opts.filters && opts.filters[0]) || {}, o = {};
      if (f.namePrefix) o.namePrefix = f.namePrefix;
      if (f.name) o.name = f.name;
      if (f.services) o.services = f.services;
      if (opts.optionalServices) o.optionalServices = opts.optionalServices;
      return init().then(function () { return BleClient.requestDevice(o); })
        .then(function (d) { return new Device(d.deviceId, d.name || ""); });
    }
  };
  Object.defineProperty(navigator, "bluetooth", { value: shim, configurable: true });
})();
