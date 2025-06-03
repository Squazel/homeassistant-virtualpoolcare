import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class PoolReadingsBarCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 20px;
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 12px);
        box-shadow: var(--ha-card-box-shadow, var(--paper-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14)));
        border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      }

      .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
      }

      .header-icon {
        width: 24px;
        height: 24px;
        margin-right: 12px;
        color: var(--primary-text-color);
      }

      .header-text {
        flex: 1;
      }

      .header-title {
        font-size: 1.1em;
        font-weight: 600;
        color: var(--primary-text-color);
        margin: 0;
      }

      .header-subtitle {
        font-size: 0.9em;
        color: var(--secondary-text-color);
        margin: 2px 0 0 0;
      }

      .reading-row {
        display: flex;
        align-items: center;
        margin-bottom: 24px;
        min-height: 40px;
      }

      .reading-row:last-child {
        margin-bottom: 0;
      }

      .reading-label {
        width: 90px;
        font-weight: 500;
        color: var(--primary-text-color);
        font-size: 0.95em;
        flex-shrink: 0;
      }

      .bar-container {
        flex: 1;
        position: relative;
        height: 20px;
        margin: 0 16px;
      }

      .bar-track {
        width: 100%;
        height: 100%;
        border-radius: 10px;
        overflow: hidden;
        position: relative;
        display: flex;
      }

      .bar-segment {
        height: 100%;
        flex: none;
      }

      .value-bubble {
        position: absolute;
        top: -8px;
        transform: translateX(-50%);
        background: var(--primary-color);
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        white-space: nowrap;
        z-index: 10;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      }

      .value-bubble::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid var(--primary-color);
      }

      .scale-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
        font-size: 0.75em;
        color: var(--secondary-text-color);
        padding: 0 8px;
      }

      .temperature-bubble { background: #ff9800; }
      .temperature-bubble::after { border-top-color: #ff9800; }

      .ph-bubble { background: #ff9800; }
      .ph-bubble::after { border-top-color: #ff9800; }

      .orp-bubble { background: #2196f3; }
      .orp-bubble::after { border-top-color: #2196f3; }

      .salinity-bubble { background: #2196f3; }
      .salinity-bubble::after { border-top-color: #2196f3; }

      .no-data {
        text-align: center;
        color: var(--secondary-text-color);
        font-style: italic;
        padding: 20px;
      }

      .thermometer-icon {
        fill: currentColor;
      }
    `;
  }

  setConfig(config) {
    if (!config.device_serial) {
      throw new Error("You must specify device_serial in configuration");
    }
    this.config = {
      device_serial: config.device_serial,
      title: config.title || "Latest measurement",
      show_timestamp: config.show_timestamp !== false,
      ...config,
    };
  }

  getSensorValue(readingName) {
    const entityId = `sensor.virtualpoolcare_${this.config.device_serial}_${readingName}`;
    const entity = this.hass.states[entityId];
    return entity ? parseFloat(entity.state) : null;
  }

  getSensorAttributes(readingName) {
    const entityId = `sensor.virtualpoolcare_${this.config.device_serial}_${readingName}`;
    const entity = this.hass.states[entityId];
    return entity ? entity.attributes : {};
  }

  getReadingConfig(readingName) {
    const attributes = this.getSensorAttributes(readingName);
    
    return {
      gauge_min: attributes.gauge_min,
      gauge_max: attributes.gauge_max,
      ok_min: attributes.ok_min,
      ok_max: attributes.ok_max,
      warning_low: attributes.warning_low,
      warning_high: attributes.warning_high,
      expired: attributes.expired || false,
      timestamp: attributes.timestamp,
      last_measurement: attributes.last_measurement,
      data_freshness: attributes.data_freshness
    };
  }

  createSegments(config) {
    if (config.gauge_min === undefined || config.gauge_max === undefined) {
      return [];
    }

    const { gauge_min, gauge_max, ok_min, ok_max, warning_low, warning_high } = config;
    const totalRange = gauge_max - gauge_min;
    const segments = [];

    // Red zone (below warning_low)
    if (warning_low > gauge_min) {
      segments.push({
        start: gauge_min,
        end: warning_low,
        color: "#f44336",
        width: ((warning_low - gauge_min) / totalRange) * 100
      });
    }

    // Orange zone (warning_low to ok_min)
    if (ok_min > warning_low) {
      segments.push({
        start: warning_low,
        end: ok_min,
        color: "#ff9800",
        width: ((ok_min - warning_low) / totalRange) * 100
      });
    }

    // Blue zone (ok_min to ok_max) - matching the official design
    segments.push({
      start: ok_min,
      end: ok_max,
      color: "#2196f3",
      width: ((ok_max - ok_min) / totalRange) * 100
    });

    // Orange zone (ok_max to warning_high)
    if (warning_high > ok_max) {
      segments.push({
        start: ok_max,
        end: warning_high,
        color: "#ff9800",
        width: ((warning_high - ok_max) / totalRange) * 100
      });
    }

    // Red zone (above warning_high)
    if (gauge_max > warning_high) {
      segments.push({
        start: warning_high,
        end: gauge_max,
        color: "#f44336",
        width: ((gauge_max - warning_high) / totalRange) * 100
      });
    }

    return segments;
  }

  getValuePosition(value, config) {
    if (value === null || value === undefined || config.gauge_min === undefined || config.gauge_max === undefined) {
      return null;
    }
    const range = config.gauge_max - config.gauge_min;
    const position = ((value - config.gauge_min) / range) * 100;
    return Math.max(0, Math.min(100, position));
  }

  getBubbleClass(readingName, value, config) {
    // Match bubble colors to the official design
    if (value === null || config.ok_min === undefined) {
      return `${readingName}-bubble`;
    }

    // Use orange for values outside OK range, blue for values in OK range
    if (value >= config.ok_min && value <= config.ok_max) {
      return `${readingName}-bubble`; // Will use blue from CSS
    } else {
      return `${readingName}-bubble`; // Will use orange from CSS
    }
  }

  getUnitOfMeasurement(readingName) {
    const unitMapping = {
      "temperature": "°C",
      "ph": "",
      "orp": "mV", 
      "salinity": "g/l"
    };
    return unitMapping[readingName] || "";
  }

  getReadingLabel(readingName) {
    const labelMapping = {
      "temperature": "Temperature",
      "ph": "pH",
      "orp": "ORP",
      "salinity": "Salinity"
    };
    return labelMapping[readingName] || readingName;
  }

  formatTimestamp(timestamp) {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffMins = Math.floor(diffMs / (1000 * 60));
      
      if (diffMins < 60) {
        return `${diffMins} minutes ago`;
      } else if (diffHours < 24) {
        return `${diffHours} hours ago`;
      } else {
        return date.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
      }
    } catch (e) {
      return timestamp;
    }
  }

  renderReading(readingName) {
    const value = this.getSensorValue(readingName);
    const config = this.getReadingConfig(readingName);
    
    if (!config || config.gauge_min === undefined || config.gauge_max === undefined) {
      return html`
        <div class="reading-row">
          <div class="reading-label">${this.getReadingLabel(readingName)}</div>
          <div class="bar-container">
            <div style="color: var(--secondary-text-color); font-size: 0.9em;">No data available</div>
          </div>
        </div>
      `;
    }

    const segments = this.createSegments(config);
    const position = this.getValuePosition(value, config);
    const unit = this.getUnitOfMeasurement(readingName);
    const bubbleClass = this.getBubbleClass(readingName, value, config);

    return html`
      <div class="reading-row">
        <div class="reading-label">${this.getReadingLabel(readingName)}</div>
        
        <div class="bar-container">
          <div class="bar-track">
            ${segments.map(segment => html`
              <div
                class="bar-segment"
                style="width: ${segment.width}%; background-color: ${segment.color};"
              ></div>
            `)}
          </div>
          
          ${position !== null && value !== null ? html`
            <div
              class="value-bubble ${bubbleClass}"
              style="left: ${position}%;"
            >
              ${value}${unit}
            </div>
          ` : ''}
          
          <div class="scale-labels">
            <span>${config.gauge_min}</span>
            <span>${config.ok_min}</span>
            <span>${config.ok_max}</span>
            <span>${config.gauge_max}</span>
          </div>
        </div>
      </div>
    `;
  }

  getLatestTimestamp() {
    const readings = ['temperature', 'ph', 'orp', 'salinity'];
    let latestTimestamp = null;
    
    for (const reading of readings) {
      const attributes = this.getSensorAttributes(reading);
      const timestamp = attributes.timestamp || attributes.last_measurement;
      if (timestamp && (!latestTimestamp || new Date(timestamp) > new Date(latestTimestamp))) {
        latestTimestamp = timestamp;
      }
    }
    
    return latestTimestamp;
  }

  render() {
    if (!this.hass || !this.config) {
      return html`<div>Loading...</div>`;
    }

    const latestTimestamp = this.getLatestTimestamp();
    const readings = ['temperature', 'ph', 'orp', 'salinity'];

    return html`
      <div class="card-header">
        <svg class="header-icon thermometer-icon" viewBox="0 0 24 24">
          <path d="M15 13V5a3 3 0 0 0-6 0v8a5 5 0 1 0 6 0zm-3 4a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/>
        </svg>
        <div class="header-text">
          <div class="header-title">${this.config.title}</div>
          ${this.config.show_timestamp && latestTimestamp ? html`
            <div class="header-subtitle">
              ${this.formatTimestamp(latestTimestamp)} by Sigfox 🛰️
            </div>
          ` : ''}
        </div>
      </div>
      
      ${readings.map(reading => this.renderReading(reading))}
    `;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("pool-readings-bar-card", PoolReadingsBarCard);

console.info(
  `%c  VIRTUALPOOLCARE-CARD  %c  Loaded automatically with integration  `,
  "color: orange; font-weight: bold; background: black",
  "color: white; font-weight: bold; background: dimgray"
);

// Register with Home Assistant's card registry
window.customCards = window.customCards || [];
window.customCards.push({
  type: "pool-readings-bar-card",
  name: "Pool Readings Bar Card",
  description: "VirtualPoolCare pool water quality display (auto-loaded)",
  preview: true,
});