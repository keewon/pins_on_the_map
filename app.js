/**
 * Pins on the Map - Application Logic
 */

// Available colors for pin lists
const COLORS = [
    { name: 'gold', value: '#d4a853' },
    { name: 'copper', value: '#c47d4e' },
    { name: 'teal', value: '#4a9d8e' },
    { name: 'coral', value: '#e07a5f' },
    { name: 'indigo', value: '#5c6bc0' },
    { name: 'rose', value: '#d4648a' },
    { name: 'emerald', value: '#4caf50' },
    { name: 'amber', value: '#ffa726' },
    { name: 'blue', value: '#3b82f6' },
    { name: 'cyan', value: '#06b6d4' },
    { name: 'violet', value: '#8b5cf6' },
];

// Icon options for specific lists
// 서울시청 좌표 (기본 위치)
const SEOUL_CITY_HALL = { lat: 37.5666, lng: 126.9784 };

// Cookie names for storing state
const COOKIE_VISIBILITY = 'pins_visibility';
const COOKIE_COLORS = 'pins_colors';
const COOKIE_ICONS = 'pins_icons';
const COOKIE_FIRST_VISIT = 'pins_first_visit';
const COOKIE_MAP_VIEW = 'pins_map_view';
const COOKIE_THEME = 'pins_theme';
const COOKIE_EXPIRY_DAYS = 365;

// Map tile URLs (한글 라벨 지원)
const MAP_TILES = {
    // OpenStreetMap 표준 타일 - 한글 라벨 지원
    dark: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    light: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
};

/**
 * Cookie utility functions
 */
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${encodeURIComponent(JSON.stringify(value))};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i].trim();
        if (c.indexOf(nameEQ) === 0) {
            try {
                return JSON.parse(decodeURIComponent(c.substring(nameEQ.length)));
            } catch (e) {
                return null;
            }
        }
    }
    return null;
}

function saveVisibilityToCookie() {
    setCookie(COOKIE_VISIBILITY, state.listVisibility, COOKIE_EXPIRY_DAYS);
}

function loadVisibilityFromCookie() {
    return getCookie(COOKIE_VISIBILITY) || {};
}

function saveColorsToCookie() {
    setCookie(COOKIE_COLORS, state.listColors, COOKIE_EXPIRY_DAYS);
}

function loadColorsFromCookie() {
    return getCookie(COOKIE_COLORS) || {};
}

function saveIconsToCookie() {
    setCookie(COOKIE_ICONS, state.listIcons, COOKIE_EXPIRY_DAYS);
}

function loadIconsFromCookie() {
    return getCookie(COOKIE_ICONS) || {};
}

function setFirstVisitCookie() {
    setCookie(COOKIE_FIRST_VISIT, false, COOKIE_EXPIRY_DAYS);
}

function isFirstVisit() {
    return getCookie(COOKIE_FIRST_VISIT) === null;
}

function saveMapViewToCookie() {
    const center = state.map.getCenter();
    const zoom = state.map.getZoom();
    setCookie(COOKIE_MAP_VIEW, { lat: center.lat, lng: center.lng, zoom: zoom }, COOKIE_EXPIRY_DAYS);
}

function loadMapViewFromCookie() {
    return getCookie(COOKIE_MAP_VIEW);
}

function clearAllCookies() {
    const cookies = [COOKIE_VISIBILITY, COOKIE_COLORS, COOKIE_ICONS, COOKIE_FIRST_VISIT, COOKIE_MAP_VIEW, COOKIE_THEME];
    cookies.forEach(name => {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    });
}

// Theme functions
function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

function saveThemeToCookie(theme) {
    setCookie(COOKIE_THEME, theme, COOKIE_EXPIRY_DAYS);
}

function loadThemeFromCookie() {
    return getCookie(COOKIE_THEME);
}

function applyTheme(theme) {
    state.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update map tiles if map is initialized
    if (state.map && state.tileLayer) {
        state.map.removeLayer(state.tileLayer);
        state.tileLayer = L.tileLayer(MAP_TILES[theme], {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19,
        }).addTo(state.map);
    }
}

function toggleTheme() {
    const newTheme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    saveThemeToCookie(newTheme);
}

function initTheme() {
    const savedTheme = loadThemeFromCookie();
    const theme = savedTheme || getSystemTheme();
    applyTheme(theme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!loadThemeFromCookie()) {
            applyTheme(e.matches ? 'light' : 'dark');
        }
    });
}

function resetSettings() {
    if (confirm('모든 설정을 초기화하시겠습니까?\n(색상, 지역 선택, 리스트 표시 설정이 초기화됩니다)')) {
        clearAllCookies();
        location.reload();
    }
}

// 기본으로 켜져있을 리스트 ID (도서관 = 4)
const DEFAULT_VISIBLE_LIST_ID = 6;

// Application State
const state = {
    map: null,
    tileLayer: null, // Current tile layer
    theme: null, // Current theme ('light' or 'dark')
    pinLists: [],
    markers: {}, // Grouped by list id
    clusterGroups: {}, // Cluster groups per list id
    listColors: {}, // Store selected colors per list
    listIcons: {}, // Store selected icons per list (for schools)
    listVisibility: {}, // Store visibility state per list
    subwayLines: null, // GeoJSON data for subway lines
    subwayLinesLayer: null, // Leaflet layer for subway lines
    trainLines: null, // GeoJSON data for train lines
    trainLinesLayer: null, // Leaflet layer for train lines
};

// DOM Elements
const elements = {
    sidebar: null,
    mobileToggle: null,
    overlay: null,
    listContainer: null,
    map: null,
    regionModal: null,
    themeToggle: null,
};

/**
 * Initialize the application
 */
async function init() {
    // Cache DOM elements
    elements.sidebar = document.getElementById('sidebar');
    elements.mobileToggle = document.getElementById('mobileToggle');
    elements.overlay = document.getElementById('overlay');
    elements.listContainer = document.getElementById('listContainer');
    elements.map = document.getElementById('map');
    elements.regionModal = document.getElementById('regionModal');
    elements.themeToggle = document.getElementById('themeToggle');

    // Initialize theme first (before map)
    initTheme();

    // Setup event listeners
    setupEventListeners();

    // Initialize map
    initMap();

    // Load pin data
    await loadPinData();

    // Check if first visit and show modal
    if (isFirstVisit()) {
        showRegionModal();
    }
}

/**
 * Show region selection modal
 */
function showRegionModal() {
    elements.regionModal.classList.add('active');
}

/**
 * Hide region selection modal
 */
function hideRegionModal() {
    elements.regionModal.classList.remove('active');
    setFirstVisitCookie();
}

/**
 * Handle location-based region selection
 */
// 10km 반경이 보이는 줌 레벨
const ZOOM_10KM = 13;

function selectRegionByLocation() {
    hideRegionModal();
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                state.map.setView([position.coords.latitude, position.coords.longitude], ZOOM_10KM);
                onMapMove();
            },
            (error) => {
                console.warn('위치 정보를 가져올 수 없습니다:', error);
                // 위치 권한 거부 시 서울시청으로
                selectSeoulCityHall();
            }
        );
    } else {
        selectSeoulCityHall();
    }
}

function selectSeoulCityHall() {
    hideRegionModal();
    state.map.setView([SEOUL_CITY_HALL.lat, SEOUL_CITY_HALL.lng], ZOOM_10KM);
    onMapMove();
}

/**
 * Initialize Leaflet map
 */
function initMap() {
    // Load saved map view or use default
    const savedView = loadMapViewFromCookie();
    const initialCenter = savedView ? [savedView.lat, savedView.lng] : [36.5, 127.5];
    const initialZoom = savedView ? savedView.zoom : 7;

    // Create map
    state.map = L.map('map', {
        center: initialCenter,
        zoom: initialZoom,
        zoomControl: true,
    });

    // Add tile layer based on current theme
    const tileUrl = MAP_TILES[state.theme] || MAP_TILES.dark;
    state.tileLayer = L.tileLayer(tileUrl, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
    }).addTo(state.map);

    // Position zoom control
    state.map.zoomControl.setPosition('topright');

    // Add location control
    const LocationControl = L.Control.extend({
        options: { position: 'topright' },
        onAdd: function() {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-location');
            const button = L.DomUtil.create('a', 'location-button', container);
            button.href = '#';
            button.title = '내 위치로 이동';
            button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/><circle cx="12" cy="12" r="8"/></svg>';
            
            L.DomEvent.on(button, 'click', function(e) {
                L.DomEvent.preventDefault(e);
                goToMyLocation();
            });
            
            return container;
        }
    });
    state.map.addControl(new LocationControl());

    // Auto-region selection on map move
    state.map.on('moveend', onMapMove);
}

/**
 * Go to user's current location
 */
function goToMyLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                state.map.setView([position.coords.latitude, position.coords.longitude], ZOOM_10KM);
            },
            (error) => {
                console.warn('위치 정보를 가져올 수 없습니다:', error);
                alert('위치 정보를 가져올 수 없습니다. 위치 권한을 확인해주세요.');
            }
        );
    } else {
        alert('이 브라우저는 위치 정보를 지원하지 않습니다.');
    }
}

/**
 * Handle map move - auto select visible regions
 */
function onMapMove() {
    saveMapViewToCookie();
    refreshAllMarkers();
}

/**
 * Load pin data from JSON files
 */
async function loadPinData() {
    showLoading();

    try {
        // First, load the lists metadata
        const listsResponse = await fetch('data/lists.json');
        if (!listsResponse.ok) throw new Error('Failed to load lists data');
        
        const listsData = await listsResponse.json();
        
        // Load saved state from cookies
        const savedVisibility = loadVisibilityFromCookie();
        const savedColors = loadColorsFromCookie();
        const savedIcons = loadIconsFromCookie();

        // Load pins for each list from individual files
        const listPromises = listsData.lists.map(async (listMeta) => {
            try {
                const pinsResponse = await fetch(`data/${listMeta.id}.json`);
                if (!pinsResponse.ok) throw new Error(`Failed to load pins for list ${listMeta.id}`);
                const pinsData = await pinsResponse.json();
                
                return {
                    ...listMeta,
                    pins: pinsData.pins || []
                };
            } catch (error) {
                console.error(`Error loading pins for list ${listMeta.id}:`, error);
                return {
                    ...listMeta,
                    pins: []
                };
            }
        });

        state.pinLists = await Promise.all(listPromises);

        // Initialize colors, icons, and visibility for each list
        state.pinLists.forEach((list, index) => {
            // Use saved color if exists, otherwise use default from data or fallback
            state.listColors[list.id] = savedColors.hasOwnProperty(list.id)
                ? savedColors[list.id]
                : (list.color || COLORS[index % COLORS.length].value);
            // Use saved icon if exists, otherwise default to 'color'
            if (list.icons) {
                state.listIcons[list.id] = savedIcons.hasOwnProperty(list.id)
                    ? savedIcons[list.id]
                    : 'color';
            }
            // Use saved visibility if exists, otherwise default to only libraries (id 4)
            state.listVisibility[list.id] = savedVisibility.hasOwnProperty(list.id) 
                ? savedVisibility[list.id] 
                : (list.id === DEFAULT_VISIBLE_LIST_ID);
        });

        renderPinLists();
        renderAllMarkers();
        
        // Load subway lines GeoJSON
        await loadSubwayLines();
        
        // Load train lines GeoJSON
        await loadTrainLines();

    } catch (error) {
        console.error('Error loading pin data:', error);
        showError('데이터를 불러오는데 실패했습니다.');
    }
}

/**
 * Refresh all markers based on map bounds
 */
function refreshAllMarkers() {
    // Remove all existing markers
    Object.keys(state.markers).forEach(listId => {
        hideMarkers(listId);
    });
    
    // Re-render markers for visible lists
    renderAllMarkers();
    
    // Update pin counts in list items
    updatePinCounts();
}

/**
 * Update pin counts displayed in list items
 */
function updatePinCounts() {
    const bounds = state.map.getBounds();
    
    state.pinLists.forEach(list => {
        const filteredCount = list.pins.filter(pin => 
            bounds.contains([pin.lat, pin.lng])
        ).length;
        
        const countElement = document.querySelector(
            `.pin-list-item[data-list-id="${list.id}"] .pin-count`
        );
        if (countElement) {
            countElement.textContent = filteredCount;
        }
    });
}

/**
 * Render pin lists in sidebar
 */
function renderPinLists() {
    const container = elements.listContainer;
    container.innerHTML = '';
    
    const bounds = state.map.getBounds();

    state.pinLists.forEach((list) => {
        const color = state.listColors[list.id];
        const isActive = state.listVisibility[list.id];
        
        // Count pins in current view
        const filteredCount = list.pins.filter(pin => 
            bounds.contains([pin.lat, pin.lng])
        ).length;
        
        const listElement = document.createElement('div');
        listElement.className = `pin-list-item ${isActive ? 'active' : ''}`;
        listElement.style.setProperty('--list-color', color);
        listElement.dataset.listId = list.id;

        const iconOptions = list.icons;
        const currentIcon = state.listIcons[list.id] || 'color';

        listElement.innerHTML = `
            <div class="list-header">
                <label class="checkbox-wrapper">
                    <input type="checkbox" ${isActive ? 'checked' : ''} data-list-id="${list.id}">
                    <span class="checkmark">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </span>
                </label>
                <div class="list-info">
                    <div class="list-title">
                        ${list.title}
                        <span class="pin-count" style="background: ${color}">${filteredCount}</span>
                    </div>
                    <div class="list-description">${list.description}</div>
                </div>
            </div>
            ${iconOptions ? `
            <div class="icon-picker-wrapper">
                <span class="picker-label">아이콘:</span>
                <div class="icon-options">
                    ${iconOptions.map(ic => `
                        <button 
                            class="icon-option ${ic === currentIcon ? 'selected' : ''}" 
                            data-icon="${ic}"
                            data-list-id="${list.id}"
                            aria-label="${ic}"
                        >${ic === 'color' ? '색상' : ic}</button>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            <div class="color-picker-wrapper">
                <span class="picker-label">색상:</span>
                <div class="color-options">
                    ${COLORS.map(c => `
                        <button 
                            class="color-option ${c.value === color ? 'selected' : ''}" 
                            style="background: ${c.value}"
                            data-color="${c.value}"
                            data-list-id="${list.id}"
                            aria-label="색상 ${c.name}"
                        ></button>
                    `).join('')}
                </div>
            </div>
        `;

        // Event: Toggle visibility
        const checkbox = listElement.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', (e) => {
            e.stopPropagation();
            toggleListVisibility(list.id);
        });

        // Event: Icon selection
        const iconOptionsElems = listElement.querySelectorAll('.icon-option');
        iconOptionsElems.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const newIcon = option.dataset.icon;
                changeListIcon(list.id, newIcon);
            });
        });

        // Event: Color selection
        const colorOptions = listElement.querySelectorAll('.color-option');
        colorOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const newColor = option.dataset.color;
                changeListColor(list.id, newColor);
            });
        });

        // Event: Click on list item (toggle visibility)
        listElement.addEventListener('click', (e) => {
            if (e.target.closest('.checkbox-wrapper') || e.target.closest('.color-option') || e.target.closest('.icon-option')) return;
            checkbox.checked = !checkbox.checked;
            toggleListVisibility(list.id);
        });

        container.appendChild(listElement);
    });
}

/**
 * Toggle visibility of a pin list
 */
function toggleListVisibility(listId) {
    state.listVisibility[listId] = !state.listVisibility[listId];
    const isVisible = state.listVisibility[listId];

    // Save to cookie
    saveVisibilityToCookie();

    // Update UI
    const listElement = document.querySelector(`.pin-list-item[data-list-id="${listId}"]`);
    if (listElement) {
        listElement.classList.toggle('active', isVisible);
    }

    // Update markers
    if (isVisible) {
        showMarkers(listId);
    } else {
        hideMarkers(listId);
    }
    
    // Toggle subway lines when subway station list is toggled
    if (listId === 6) {
        if (isVisible) {
            showSubwayLines();
        } else {
            hideSubwayLines();
        }
    }
    
    // Toggle train lines when train station lists are toggled
    if (listId === 7 || listId === 8) {
        const anyTrainListVisible = state.listVisibility[7] || state.listVisibility[8];
        if (anyTrainListVisible) {
            showTrainLines();
        } else {
            hideTrainLines();
        }
    }
}

/**
 * Change color of a pin list
 */
function changeListColor(listId, newColor) {
    state.listColors[listId] = newColor;

    // Save to cookie
    saveColorsToCookie();

    // Update list item UI
    const listElement = document.querySelector(`.pin-list-item[data-list-id="${listId}"]`);
    if (listElement) {
        listElement.style.setProperty('--list-color', newColor);
        
        // Update pin count badge
        const pinCount = listElement.querySelector('.pin-count');
        if (pinCount) {
            pinCount.style.background = newColor;
        }

        // Update selected color indicator
        const colorOptions = listElement.querySelectorAll('.color-option');
        colorOptions.forEach(option => {
            option.classList.toggle('selected', option.dataset.color === newColor);
        });
    }

    // Update markers if visible
    if (state.listVisibility[listId]) {
        hideMarkers(listId);
        showMarkers(listId);
    }
}

/**
 * Change icon of a pin list
 */
function changeListIcon(listId, newIcon) {
    state.listIcons[listId] = newIcon;

    // Save to cookie
    saveIconsToCookie();

    // Update selected icon indicator
    const listElement = document.querySelector(`.pin-list-item[data-list-id="${listId}"]`);
    if (listElement) {
        const iconOptions = listElement.querySelectorAll('.icon-option');
        iconOptions.forEach(option => {
            option.classList.toggle('selected', option.dataset.icon === newIcon);
        });
    }

    // Update markers if visible
    if (state.listVisibility[listId]) {
        hideMarkers(listId);
        showMarkers(listId);
    }
}

/**
 * Render all markers on the map
 */
function renderAllMarkers() {
    state.pinLists.forEach(list => {
        if (state.listVisibility[list.id]) {
            showMarkers(list.id);
        }
    });
}

/**
 * Show markers for a specific list (filtered by selected regions)
 */
function showMarkers(listId) {
    const list = state.pinLists.find(l => l.id === listId);
    if (!list) return;

    const color = state.listColors[listId];
    
    // Remove existing cluster group if any
    if (state.clusterGroups[listId]) {
        state.map.removeLayer(state.clusterGroups[listId]);
    }
    
    // Create new cluster group with custom icon
    const clusterGroup = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster) {
            const count = cluster.getChildCount();
            let size = 'small';
            if (count > 50) size = 'large';
            else if (count > 10) size = 'medium';
            
            return L.divIcon({
                html: `<div class="cluster-marker cluster-${size}" style="background: ${color}"><span>${count}</span></div>`,
                className: 'custom-cluster-wrapper',
                iconSize: L.point(40, 40)
            });
        }
    });
    
    const bounds = state.map.getBounds();

    // Filter pins by map bounds
    const filteredPins = list.pins.filter(pin => 
        bounds.contains([pin.lat, pin.lng])
    );

    filteredPins.forEach(pin => {
        const marker = createMarker(pin, color, list.title, listId);
        clusterGroup.addLayer(marker);
    });
    
    clusterGroup.addTo(state.map);
    state.clusterGroups[listId] = clusterGroup;
}

/**
 * Hide markers for a specific list
 */
function hideMarkers(listId) {
    if (state.clusterGroups[listId]) {
        state.map.removeLayer(state.clusterGroups[listId]);
        delete state.clusterGroups[listId];
    }
}

/**
 * Load subway lines GeoJSON
 */
async function loadSubwayLines() {
    try {
        const response = await fetch('data/subway_lines.json');
        if (!response.ok) return;
        
        state.subwayLines = await response.json();
        console.log(`Loaded ${state.subwayLines.features.length} subway lines`);
        
        // Show subway lines if subway station list is visible
        if (state.listVisibility[6]) {
            showSubwayLines();
        }
    } catch (error) {
        console.error('Error loading subway lines:', error);
    }
}

/**
 * Show subway lines on map
 */
function showSubwayLines() {
    if (!state.subwayLines || state.subwayLinesLayer) return;
    
    state.subwayLinesLayer = L.geoJSON(state.subwayLines, {
        style: function(feature) {
            const isDashed = feature.properties.dashed === true;
            return {
                color: feature.properties.colour || '#888888',
                weight: isDashed ? 4 : 3,
                opacity: 0.8,
                dashArray: isDashed ? '10, 10' : null
            };
        },
        onEachFeature: function(feature, layer) {
            if (feature.properties.name) {
                layer.bindTooltip(feature.properties.name, {
                    permanent: false,
                    direction: 'top'
                });
            }
        }
    });
    
    // Add to map below markers
    state.subwayLinesLayer.addTo(state.map);
    state.subwayLinesLayer.bringToBack();
}

/**
 * Hide subway lines from map
 */
function hideSubwayLines() {
    if (state.subwayLinesLayer) {
        state.map.removeLayer(state.subwayLinesLayer);
        state.subwayLinesLayer = null;
    }
}

/**
 * Load train lines GeoJSON
 */
async function loadTrainLines() {
    try {
        const response = await fetch('data/train_lines.json');
        if (!response.ok) return;
        
        state.trainLines = await response.json();
        console.log(`Loaded ${state.trainLines.features.length} train lines`);
        
        // Show train lines if either train station list is visible
        if (state.listVisibility[7] || state.listVisibility[8]) {
            showTrainLines();
        }
    } catch (error) {
        console.error('Error loading train lines:', error);
    }
}

/**
 * Show train lines on map
 */
function showTrainLines() {
    if (!state.trainLines || state.trainLinesLayer) return;
    
    state.trainLinesLayer = L.geoJSON(state.trainLines, {
        style: function(feature) {
            const isDashed = feature.properties.dashed === true;
            return {
                color: feature.properties.colour || '#666666',
                weight: isDashed ? 4 : 3,
                opacity: 0.7,
                dashArray: isDashed ? '10, 10' : null
            };
        },
        onEachFeature: function(feature, layer) {
            if (feature.properties.name) {
                layer.bindTooltip(feature.properties.name, {
                    permanent: false,
                    direction: 'top'
                });
            }
        }
    });
    
    // Add to map below markers
    state.trainLinesLayer.addTo(state.map);
    state.trainLinesLayer.bringToBack();
}

/**
 * Hide train lines from map
 */
function hideTrainLines() {
    if (state.trainLinesLayer) {
        state.map.removeLayer(state.trainLinesLayer);
        state.trainLinesLayer = null;
    }
}

/**
 * Create a custom marker
 */
function createMarker(pin, color, listTitle, listId) {
    let icon;
    const list = state.pinLists.find(l => l.id === listId);
    
    // 지하철역은 심플한 동그라미로 표시
    if (listId === 6) {
        const isTransfer = pin.description && pin.description.includes(',');
        const markerClass = isTransfer ? 'subway-marker transfer' : 'subway-marker';
        icon = L.divIcon({
            className: 'subway-marker-wrapper',
            html: `<div class="${markerClass}" style="background: ${color}"></div>`,
            iconSize: [isTransfer ? 18 : 14, isTransfer ? 18 : 14],
            iconAnchor: [isTransfer ? 9 : 7, isTransfer ? 9 : 7],
            popupAnchor: [0, isTransfer ? -9 : -7],
        });
    } else if (listId === 7 || listId === 8) {
        // 기차역은 정사각형으로 표시
        icon = L.divIcon({
            className: 'train-marker-wrapper',
            html: `<div class="train-marker" style="background: ${color}"></div>`,
            iconSize: [16, 16],
            iconAnchor: [8, 8],
            popupAnchor: [0, -8],
        });
    } else if (list && list.icons) {
        // 아이콘 옵션이 있는 리스트는 선택된 아이콘에 따라 표시
        const selectedIcon = state.listIcons[listId] || 'color';
        if (selectedIcon === 'color') {
            // 기본 마커 (핀 모양)
            icon = L.divIcon({
                className: 'custom-marker-wrapper',
                html: `<div class="custom-marker" style="background: ${color}"></div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32],
            });
        } else if (['🏫', '🍔', '🥪', '📚', '🏊', '☕', '🥐', '🏢'].includes(selectedIcon)) {
            // 이모지 마커
            icon = L.divIcon({
                className: 'emoji-marker-wrapper',
                html: `<div class="emoji-marker">${selectedIcon}</div>`,
                iconSize: [28, 28],
                iconAnchor: [14, 14],
                popupAnchor: [0, -14],
            });
        } else {
            // 텍스트 마커 (중, 中, 고, 高)
            icon = L.divIcon({
                className: 'text-marker-wrapper',
                html: `<div class="text-marker" style="background: ${color}">${selectedIcon}</div>`,
                iconSize: [28, 28],
                iconAnchor: [14, 14],
                popupAnchor: [0, -14],
            });
        }
    } else {
        // 기본 마커 (핀 모양)
        icon = L.divIcon({
            className: 'custom-marker-wrapper',
            html: `<div class="custom-marker" style="background: ${color}"></div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
        });
    }

    const marker = L.marker([pin.lat, pin.lng], { icon });

    // Title with optional Kakao Map link
    const titleContent = pin.url 
        ? `<a href="${pin.url}" target="_blank" rel="noopener noreferrer" class="popup-title-link">${pin.title}</a>`
        : `<span>${pin.title}</span>`;

    // 학교 상세정보 (중학교, 고등학교)
    let schoolInfoHtml = '';
    if ((listId === 1 || listId === 9) && (pin.coed_type || pin.school_type)) {
        const badges = [];
        
        // 학교유형 (고등학교만: 일반고/자사고/특목고/특성화고 등)
        if (listId === 9 && pin.school_type) {
            const typeColors = {
                '일반고': 'general',
                '자사고': 'autonomous',
                '자공고': 'autonomous',
                '특목고': 'special',
                '과학고': 'special',
                '외고': 'special',
                '국제고': 'special',
                '예술고': 'special',
                '체육고': 'special',
                '마이스터고': 'special',
                '특성화고': 'vocational',
                '실업계': 'vocational',
            };
            const typeClass = typeColors[pin.school_type] || 'general';
            badges.push(`<span class="school-badge ${typeClass}">${pin.school_type}</span>`);
        }
        
        // 남/녀/공학 배지
        if (pin.coed_type === '남학교') {
            badges.push('<span class="school-badge male">♂ 남</span>');
        } else if (pin.coed_type === '여학교') {
            badges.push('<span class="school-badge female">♀ 여</span>');
        } else if (pin.coed_type === '공학') {
            badges.push('<span class="school-badge coed">공학</span>');
        }
        
        // 설립유형 (공립/사립)
        if (pin.found_type) {
            badges.push(`<span class="school-badge found">${pin.found_type}</span>`);
        }
        
        // 학생수 (남/녀 별도 표시)
        if (pin.student_total) {
            if (pin.student_male > 0 || pin.student_female > 0) {
                badges.push(`<span class="school-badge students">👨‍🎓 ${pin.student_total}명 (♂${pin.student_male} ♀${pin.student_female})</span>`);
            } else {
                badges.push(`<span class="school-badge students">👨‍🎓 ${pin.student_total}명</span>`);
            }
        }
        
        // 진학률 (고등학교만)
        if (listId === 9 && pin.advancement_rate) {
            badges.push(`<span class="school-badge rate">📈 진학률 ${pin.advancement_rate}%</span>`);
        }
        
        if (badges.length > 0) {
            schoolInfoHtml = `<div class="school-info">${badges.join('')}</div>`;
        }
    }

    const popupContent = `
        <div class="popup-content">
            <div class="popup-title">${titleContent}</div>
            <div class="popup-description">${pin.description}</div>
            ${schoolInfoHtml}
            <div class="popup-list-badge" style="background: ${color}">${listTitle}</div>
        </div>
    `;

    marker.bindPopup(popupContent, {
        maxWidth: 280,
        closeButton: true,
    });

    return marker;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Mobile toggle (hamburger button)
    elements.mobileToggle.addEventListener('click', toggleSidebar);

    // Sidebar header close button
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', closeSidebar);
    }

    // Theme toggle
    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleTheme);
    }

    // Overlay click closes sidebar
    elements.overlay.addEventListener('click', closeSidebar);

    // Close sidebar on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeSidebar();
            hideRegionModal();
        }
    });

    // Handle window resize
    window.addEventListener('resize', handleResize);

    // Region modal buttons
    document.getElementById('btnLocationBased').addEventListener('click', selectRegionByLocation);
    document.getElementById('btnSeoulCityHall').addEventListener('click', selectSeoulCityHall);

    // Reset settings button
    document.getElementById('resetSettings').addEventListener('click', resetSettings);
}

/**
 * Toggle sidebar (mobile)
 */
function toggleSidebar() {
    const isOpen = elements.sidebar.classList.contains('open');
    if (isOpen) {
        closeSidebar();
    } else {
        openSidebar();
    }
}

/**
 * Open sidebar
 */
function openSidebar() {
    elements.sidebar.classList.add('open');
    elements.mobileToggle.classList.add('active');
    elements.overlay.classList.add('active');
    document.body.classList.add('sidebar-open');
    document.body.style.overflow = 'hidden';
}

/**
 * Close sidebar
 */
function closeSidebar() {
    elements.sidebar.classList.remove('open');
    elements.mobileToggle.classList.remove('active');
    elements.overlay.classList.remove('active');
    document.body.classList.remove('sidebar-open');
    document.body.style.overflow = '';
}

/**
 * Handle window resize
 */
function handleResize() {
    if (window.innerWidth > 768) {
        closeSidebar();
    }
    // Invalidate map size on resize
    if (state.map) {
        state.map.invalidateSize();
    }
}

/**
 * Show loading state
 */
function showLoading() {
    elements.listContainer.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>데이터를 불러오는 중...</p>
        </div>
    `;
}

/**
 * Show error state
 */
function showError(message) {
    elements.listContainer.innerHTML = `
        <div class="loading">
            <p style="color: #e07a5f;">⚠️ ${message}</p>
        </div>
    `;
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
