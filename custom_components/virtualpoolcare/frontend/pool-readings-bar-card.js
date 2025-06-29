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
        margin-bottom: 36px;
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
        padding-top: 18px;
      }

      .bar-track {
        width: 100%;
        height: 20px;
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
        top: -12px;
        transform: translateX(-50%);
        background: var(--primary-color);
        color: white;
        padding: 4px 10px; /* Reduced from 6px to 4px for shorter height */
        border-radius: 12px;
        font-size: 0.75em; /* Reduced from 0.8em to 0.75em */
        font-weight: 600;
        white-space: nowrap;
        z-index: 10;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        min-width: 40px;
        text-align: center;
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
        margin-top: 6px;
        font-size: 0.75em;
        color: var(--secondary-text-color);
        padding: 0 8px;
      }

      /* Bubble colors based on range position */
      .red-bubble { background: #f44336; }
      .red-bubble::after { border-top-color: #f44336; }

      .orange-bubble { background: #ff9800; }
      .orange-bubble::after { border-top-color: #ff9800; }

      .blue-bubble { background: #2196f3; }
      .blue-bubble::after { border-top-color: #2196f3; }

      .default-bubble { background: var(--primary-color); }
      .default-bubble::after { border-top-color: var(--primary-color); }

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
    this.config = {
      device_serial: config.device_serial || null, // Make optional
      title: config.title || "Latest measurement",
      show_timestamp: config.show_timestamp !== false,
      ...config,
    };
    
    // No error thrown if device_serial is missing - we'll auto-detect
  }

  findVirtualPoolCareEntities() {
    // Look for any entities that contain virtualpoolcare and our reading types
    const allEntities = Object.keys(this.hass.states);
    const poolEntities = allEntities.filter(id => 
      id.includes('virtualpoolcare') && 
      (id.includes('temperature') || id.includes('ph') || id.includes('orp') || id.includes('salinity'))
    );
    
    console.log("All entities containing 'virtualpoolcare':", allEntities.filter(id => id.includes('virtualpoolcare')));
    console.log("Pool reading entities found:", poolEntities);
    
    // Auto-detect device serial from first entity if not configured
    if (!this.config.device_serial && poolEntities.length > 0) {
      const match = poolEntities[0].match(/sensor\.virtualpoolcare_([^_]+)_/);
      if (match) {
        this.config.device_serial = match[1];
        console.log("Auto-detected device serial:", this.config.device_serial);
      }
    }
    
    return poolEntities;
  }

  getSensorValue(readingName) {
    // Auto-detect entities if no device serial configured
    if (!this.config.device_serial) {
      this.findVirtualPoolCareEntities();
    }
    
    // First try the expected pattern with configured/detected device serial
    if (this.config.device_serial) {
      const entityId = `sensor.virtualpoolcare_${this.config.device_serial}_${readingName}`;
      let entity = this.hass.states[entityId];
      
      if (entity) {
        console.log(`Found entity with expected pattern: ${entityId}`);
        return parseFloat(entity.state);
      }
      
      // Try lowercase serial
      const entityIdLower = `sensor.virtualpoolcare_${this.config.device_serial.toLowerCase()}_${readingName}`;
      entity = this.hass.states[entityIdLower];
      
      if (entity) {
        console.log(`Found entity with lowercase serial: ${entityIdLower}`);
        return parseFloat(entity.state);
      }
    }
    
    // Fallback: search for any entity containing both virtualpoolcare and the reading name
    const allEntities = Object.keys(this.hass.states);
    const matchingEntity = allEntities.find(id => 
      id.includes('virtualpoolcare') && 
      id.includes(readingName) &&
      id.startsWith('sensor.')
    );
    
    if (matchingEntity) {
      console.log(`Found entity by search: ${matchingEntity} for reading: ${readingName}`);
      return parseFloat(this.hass.states[matchingEntity].state);
    }
    
    console.log(`No entity found for reading: ${readingName}`);
    return null;
  }

  getSensorAttributes(readingName) {
    // Auto-detect entities if no device serial configured
    if (!this.config.device_serial) {
      this.findVirtualPoolCareEntities();
    }
    
    // Same logic as getSensorValue but return attributes
    if (this.config.device_serial) {
      const entityId = `sensor.virtualpoolcare_${this.config.device_serial}_${readingName}`;
      let entity = this.hass.states[entityId];
      
      if (entity) {
        return entity.attributes;
      }
      
      // Try lowercase serial
      const entityIdLower = `sensor.virtualpoolcare_${this.config.device_serial.toLowerCase()}_${readingName}`;
      entity = this.hass.states[entityIdLower];
      
      if (entity) {
        return entity.attributes;
      }
    }
    
    // Fallback: search for any entity
    const allEntities = Object.keys(this.hass.states);
    const matchingEntity = allEntities.find(id => 
      id.includes('virtualpoolcare') && 
      id.includes(readingName) &&
      id.startsWith('sensor.')
    );
    
    if (matchingEntity) {
      return this.hass.states[matchingEntity].attributes;
    }
    
    return {};
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
    // Check if value is out of range first
    if (value !== null && config.gauge_min !== undefined && config.gauge_max !== undefined) {
      if (value < config.gauge_min || value > config.gauge_max) {
        return 'red-bubble';
      }
    }

    if (value === null || config.ok_min === undefined) {
      return 'default-bubble';
    }

    // Return color based on which range the value falls into
    if (value < config.warning_low) {
      return 'red-bubble';
    } else if (value < config.ok_min) {
      return 'orange-bubble';
    } else if (value <= config.ok_max) {
      return 'blue-bubble';
    } else if (value <= config.warning_high) {
      return 'orange-bubble';
    } else {
      return 'red-bubble';
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
      
      const locale = this.hass?.locale?.language || navigator.language || 'en-US';
      
      if (diffMins < 60) {
        return `${diffMins} minutes ago`;
      } else if (diffHours < 24) {
        return `${diffHours} hours ago`;
      } else {
        return date.toLocaleDateString(locale, { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit'
        });
      }
    } catch (e) {
      return timestamp;
    }
  }

  formatNumberForDisplay(value) {
    const num = parseFloat(value);
    if (isNaN(num)) {
      return ''; // Return empty string if not a valid number
    }
    // Round to 2 decimal places
    return Math.round(num * 100) / 100;
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

    // Calculate positions for threshold labels
    // TODO: consider options if labels may overlap - either stagger or suppress some
    const totalRange = config.gauge_max - config.gauge_min;
    const warningLowPos = ((config.warning_low - config.gauge_min) / totalRange) * 100;
    const okMinPos = ((config.ok_min - config.gauge_min) / totalRange) * 100;
    const okMaxPos = ((config.ok_max - config.gauge_min) / totalRange) * 100;
    const warningHighPos = ((config.warning_high - config.gauge_min) / totalRange) * 100;

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
              ${this.formatNumberForDisplay(value)}${unit}
            </div>
          ` : ''}
          
          <div class="scale-labels">
            <span style="position: absolute; left: ${warningLowPos}%; transform: translateX(-50%);">${this.formatNumberForDisplay(config.warning_low)}</span>
            <span style="position: absolute; left: ${okMinPos}%; transform: translateX(-50%);">${this.formatNumberForDisplay(config.ok_min)}</span>
            <span style="position: absolute; left: ${okMaxPos}%; transform: translateX(-50%);">${this.formatNumberForDisplay(config.ok_max)}</span>
            <span style="position: absolute; left: ${warningHighPos}%; transform: translateX(-50%);">${this.formatNumberForDisplay(config.warning_high)}</span>
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

    // Debug: Show what entities we're working with
    const availableEntities = this.findVirtualPoolCareEntities();
    
    if (availableEntities.length === 0) {
      return html`
        <div class="card-header">
          <div class="header-text">
            <div class="header-title">${this.config.title}</div>
          </div>
        </div>
        <div class="no-data">
          No VirtualPoolCare sensor entities found. Make sure your VirtualPoolCare integration is set up and working.
        </div>
      `;
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
              ${this.formatTimestamp(latestTimestamp)}
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
  `%c  POOL-READINGS-BAR-CARD  %c  Loaded automatically with integration  `,
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