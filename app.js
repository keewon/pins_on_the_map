/**
 * Pins in the Map - Application Logic
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
];

// 광역단체 목록
const REGIONS = [
    "서울특별시",
    "부산광역시",
    "대구광역시",
    "인천광역시",
    "광주광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "경기도",
    "강원특별자치도",
    "충청북도",
    "충청남도",
    "전북특별자치도",
    "전라남도",
    "경상북도",
    "경상남도",
    "제주특별자치도",
];

// 지역 이름 축약
const REGION_SHORT_NAMES = {
    "서울특별시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "광주광역시": "광주",
    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",
    "경기도": "경기",
    "강원특별자치도": "강원",
    "충청북도": "충북",
    "충청남도": "충남",
    "전북특별자치도": "전북",
    "전라남도": "전남",
    "경상북도": "경북",
    "경상남도": "경남",
    "제주특별자치도": "제주",
};

function shortenRegionName(region) {
    return REGION_SHORT_NAMES[region] || region;
}

// 광역단체별 중심 좌표 (위치 기반 선택용)
const REGION_CENTERS = {
    "서울특별시": { lat: 37.5665, lng: 126.978 },
    "부산광역시": { lat: 35.1796, lng: 129.0756 },
    "대구광역시": { lat: 35.8714, lng: 128.6014 },
    "인천광역시": { lat: 37.4563, lng: 126.7052 },
    "광주광역시": { lat: 35.1595, lng: 126.8526 },
    "대전광역시": { lat: 36.3504, lng: 127.3845 },
    "울산광역시": { lat: 35.5384, lng: 129.3114 },
    "세종특별자치시": { lat: 36.4800, lng: 127.2890 },
    "경기도": { lat: 37.4138, lng: 127.5183 },
    "강원특별자치도": { lat: 37.8228, lng: 128.1555 },
    "충청북도": { lat: 36.6357, lng: 127.4917 },
    "충청남도": { lat: 36.5184, lng: 126.8000 },
    "전북특별자치도": { lat: 35.8203, lng: 127.1089 },
    "전라남도": { lat: 34.8679, lng: 126.9910 },
    "경상북도": { lat: 36.4919, lng: 128.8889 },
    "경상남도": { lat: 35.4606, lng: 128.2132 },
    "제주특별자치도": { lat: 33.4890, lng: 126.4983 },
};

// Cookie names for storing state
const COOKIE_VISIBILITY = 'pins_visibility';
const COOKIE_COLORS = 'pins_colors';
const COOKIE_REGIONS = 'pins_regions';
const COOKIE_FIRST_VISIT = 'pins_first_visit';
const COOKIE_EXPIRY_DAYS = 365;

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

function saveRegionsToCookie() {
    setCookie(COOKIE_REGIONS, state.selectedRegions, COOKIE_EXPIRY_DAYS);
}

function loadRegionsFromCookie() {
    return getCookie(COOKIE_REGIONS) || null;
}

function setFirstVisitCookie() {
    setCookie(COOKIE_FIRST_VISIT, false, COOKIE_EXPIRY_DAYS);
}

function isFirstVisit() {
    return getCookie(COOKIE_FIRST_VISIT) === null;
}

// 기본으로 켜져있을 리스트 ID (도서관 = 4)
const DEFAULT_VISIBLE_LIST_ID = 4;

// Application State
const state = {
    map: null,
    pinLists: [],
    markers: {}, // Grouped by list id
    listColors: {}, // Store selected colors per list
    listVisibility: {}, // Store visibility state per list
    selectedRegions: [], // Store selected regions
    regionCounts: {}, // Pin counts per region
    regionFilterCollapsed: false,
    radiusMode: false, // 20km 반경 모드
    userLocation: null, // 사용자 위치
    radiusCircle: null, // 반경 표시 원
};

// DOM Elements
const elements = {
    sidebar: null,
    mobileToggle: null,
    overlay: null,
    listContainer: null,
    map: null,
    regionModal: null,
    regionChips: null,
    regionToggleBtn: null,
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
    elements.regionChips = document.getElementById('regionChips');
    elements.regionToggleBtn = document.getElementById('regionToggleBtn');

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
function selectRegionByLocation() {
    hideRegionModal();
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                const closestRegion = findClosestRegion(userLat, userLng);
                
                state.selectedRegions = [closestRegion];
                saveRegionsToCookie();
                renderRegionChips();
                refreshAllMarkers();
                
                // Center map on the region
                const center = REGION_CENTERS[closestRegion];
                state.map.setView([center.lat, center.lng], 10);
            },
            (error) => {
                console.warn('위치 정보를 가져올 수 없습니다:', error);
                // Fallback to Seoul
                selectSeoulOnly();
            }
        );
    } else {
        // Fallback to Seoul
        selectSeoulOnly();
    }
}

/**
 * Select Seoul only
 */
function selectSeoulOnly() {
    hideRegionModal();
    state.selectedRegions = ['서울특별시'];
    saveRegionsToCookie();
    renderRegionChips();
    refreshAllMarkers();
    
    // Center map on Seoul
    state.map.setView([37.5665, 126.978], 11);
}

/**
 * Select all regions
 */
function selectAllRegions() {
    hideRegionModal();
    state.selectedRegions = [...REGIONS];
    saveRegionsToCookie();
    renderRegionChips();
    refreshAllMarkers();
}

/**
 * Find closest region to user location
 */
function findClosestRegion(userLat, userLng) {
    let closestRegion = REGIONS[0];
    let minDistance = Infinity;

    for (const region of REGIONS) {
        const center = REGION_CENTERS[region];
        const distance = Math.sqrt(
            Math.pow(userLat - center.lat, 2) + Math.pow(userLng - center.lng, 2)
        );
        if (distance < minDistance) {
            minDistance = distance;
            closestRegion = region;
        }
    }

    return closestRegion;
}

/**
 * Calculate distance between two coordinates in kilometers (Haversine formula)
 */
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

/**
 * Toggle 20km radius mode
 */
function toggle20kmRadius() {
    if (state.radiusMode) {
        // Turn off radius mode
        state.radiusMode = false;
        state.userLocation = null;
        
        // Remove radius circle
        if (state.radiusCircle) {
            state.map.removeLayer(state.radiusCircle);
            state.radiusCircle = null;
        }
        
        renderRegionChips();
        refreshAllMarkers();
        updatePinCounts();
    } else {
        // Turn on radius mode
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    state.radiusMode = true;
                    state.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    
                    // Add radius circle to map
                    if (state.radiusCircle) {
                        state.map.removeLayer(state.radiusCircle);
                    }
                    state.radiusCircle = L.circle(
                        [state.userLocation.lat, state.userLocation.lng],
                        {
                            radius: 20000, // 20km in meters
                            color: '#4a9d8e',
                            fillColor: '#4a9d8e',
                            fillOpacity: 0.1,
                            weight: 2
                        }
                    ).addTo(state.map);
                    
                    // Center map on user location
                    state.map.setView([state.userLocation.lat, state.userLocation.lng], 11);
                    
                    renderRegionChips();
                    refreshAllMarkers();
                    updatePinCounts();
                },
                (error) => {
                    console.warn('위치 정보를 가져올 수 없습니다:', error);
                    alert('위치 정보를 가져올 수 없습니다. 위치 권한을 확인해주세요.');
                }
            );
        } else {
            alert('이 브라우저에서는 위치 기능을 지원하지 않습니다.');
        }
    }
}

/**
 * Check if a pin is within 20km radius
 */
function isPinInRadius(pin) {
    if (!state.radiusMode || !state.userLocation) {
        return true; // Not in radius mode, show all
    }
    
    const distance = calculateDistance(
        state.userLocation.lat,
        state.userLocation.lng,
        pin.latitude,
        pin.longitude
    );
    
    return distance <= 20;
}

/**
 * Initialize Leaflet map
 */
function initMap() {
    // Create map centered on South Korea
    state.map = L.map('map', {
        center: [36.5, 127.5],
        zoom: 7,
        zoomControl: true,
    });

    // Add tile layer (CartoDB dark matter for dark theme)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
    }).addTo(state.map);

    // Position zoom control
    state.map.zoomControl.setPosition('topright');
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
        const savedRegions = loadRegionsFromCookie();

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

        // Calculate region counts
        calculateRegionCounts();

        // Initialize regions (from cookie or default to Seoul)
        if (savedRegions) {
            state.selectedRegions = savedRegions;
        } else if (!isFirstVisit()) {
            // Not first visit but no saved regions - default to all
            state.selectedRegions = [...REGIONS];
        }
        // If first visit, modal will handle region selection

        // Initialize colors and visibility for each list
        state.pinLists.forEach((list, index) => {
            // Use saved color if exists, otherwise use default from data or fallback
            state.listColors[list.id] = savedColors.hasOwnProperty(list.id)
                ? savedColors[list.id]
                : (list.color || COLORS[index % COLORS.length].value);
            // Use saved visibility if exists, otherwise default to only libraries (id 4)
            state.listVisibility[list.id] = savedVisibility.hasOwnProperty(list.id) 
                ? savedVisibility[list.id] 
                : (list.id === DEFAULT_VISIBLE_LIST_ID);
        });

        renderRegionChips();
        renderPinLists();
        
        // Only render markers if regions are selected (not first visit waiting for modal)
        if (state.selectedRegions.length > 0) {
            renderAllMarkers();
        }

    } catch (error) {
        console.error('Error loading pin data:', error);
        showError('데이터를 불러오는데 실패했습니다.');
    }
}

/**
 * Calculate pin counts per region
 */
function calculateRegionCounts() {
    state.regionCounts = {};
    
    // Initialize all regions with 0
    REGIONS.forEach(region => {
        state.regionCounts[region] = 0;
    });

    // Count pins per region across all lists
    state.pinLists.forEach(list => {
        list.pins.forEach(pin => {
            const region = pin.region || '기타';
            if (state.regionCounts.hasOwnProperty(region)) {
                state.regionCounts[region]++;
            }
        });
    });
}

/**
 * Render region chips
 */
function renderRegionChips() {
    const container = elements.regionChips;
    container.innerHTML = '';

    REGIONS.forEach(region => {
        const count = state.regionCounts[region] || 0;
        const isActive = state.selectedRegions.includes(region);
        
        const chip = document.createElement('button');
        chip.className = `region-chip ${isActive ? 'active' : ''}`;
        chip.innerHTML = `
            ${shortenRegionName(region)}
            <span class="region-count">(${count})</span>
        `;
        chip.addEventListener('click', () => toggleRegion(region));
        
        container.appendChild(chip);
    });

    // Add action buttons to separate container
    const actionsContainer = document.getElementById('regionActions');
    actionsContainer.innerHTML = `
        <button class="region-action-btn ${state.radiusMode ? 'active' : ''}" id="toggle20kmRadius">
            📍 20km 반경
        </button>
        <button class="region-action-btn" id="selectAllRegions">전체 선택</button>
        <button class="region-action-btn" id="clearAllRegions">전체 해제</button>
    `;

    // Add event listeners
    document.getElementById('toggle20kmRadius').addEventListener('click', toggle20kmRadius);

    document.getElementById('selectAllRegions').addEventListener('click', () => {
        state.selectedRegions = [...REGIONS];
        saveRegionsToCookie();
        renderRegionChips();
        refreshAllMarkers();
    });

    document.getElementById('clearAllRegions').addEventListener('click', () => {
        state.selectedRegions = [];
        saveRegionsToCookie();
        renderRegionChips();
        refreshAllMarkers();
    });
}

/**
 * Toggle region selection
 */
function toggleRegion(region) {
    const index = state.selectedRegions.indexOf(region);
    if (index === -1) {
        state.selectedRegions.push(region);
    } else {
        state.selectedRegions.splice(index, 1);
    }
    
    saveRegionsToCookie();
    renderRegionChips();
    refreshAllMarkers();
}

/**
 * Refresh all markers based on current region selection
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
    state.pinLists.forEach(list => {
        const filteredCount = list.pins.filter(pin => {
            const regionOk = state.radiusMode || state.selectedRegions.includes(pin.region || '기타');
            const radiusOk = isPinInRadius(pin);
            return regionOk && radiusOk;
        }).length;
        
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

    state.pinLists.forEach((list) => {
        const color = state.listColors[list.id];
        const isActive = state.listVisibility[list.id];
        
        // Count pins in selected regions/radius
        const filteredCount = list.pins.filter(pin => {
            const regionOk = state.radiusMode || state.selectedRegions.includes(pin.region || '기타');
            const radiusOk = isPinInRadius(pin);
            return regionOk && radiusOk;
        }).length;
        
        const listElement = document.createElement('div');
        listElement.className = `pin-list-item ${isActive ? 'active' : ''}`;
        listElement.style.setProperty('--list-color', color);
        listElement.dataset.listId = list.id;

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
            <div class="color-picker-wrapper">
                <span class="color-picker-label">색상:</span>
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
            if (e.target.closest('.checkbox-wrapper') || e.target.closest('.color-option')) return;
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
    state.markers[listId] = [];

    // Filter pins by selected regions and radius
    const filteredPins = list.pins.filter(pin => {
        // Check region filter (skip if in radius mode)
        const regionOk = state.radiusMode || state.selectedRegions.includes(pin.region || '기타');
        // Check radius filter
        const radiusOk = isPinInRadius(pin);
        return regionOk && radiusOk;
    });

    filteredPins.forEach(pin => {
        const marker = createMarker(pin, color, list.title);
        marker.addTo(state.map);
        state.markers[listId].push(marker);
    });
}

/**
 * Hide markers for a specific list
 */
function hideMarkers(listId) {
    if (state.markers[listId]) {
        state.markers[listId].forEach(marker => {
            state.map.removeLayer(marker);
        });
        state.markers[listId] = [];
    }
}

/**
 * Create a custom marker
 */
function createMarker(pin, color, listTitle) {
    // Create custom icon
    const icon = L.divIcon({
        className: 'custom-marker-wrapper',
        html: `<div class="custom-marker" style="background: ${color}"></div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
    });

    const marker = L.marker([pin.latitude, pin.longitude], { icon });

    // Title with optional Kakao Map link
    const titleContent = pin.url 
        ? `<a href="${pin.url}" target="_blank" rel="noopener noreferrer" class="popup-title-link">${pin.title}</a>`
        : `<span>${pin.title}</span>`;

    const popupContent = `
        <div class="popup-content">
            <div class="popup-title">${titleContent}</div>
            <div class="popup-description">${pin.description}</div>
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
    // Mobile toggle
    elements.mobileToggle.addEventListener('click', toggleSidebar);

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
    document.getElementById('btnSeoulOnly').addEventListener('click', selectSeoulOnly);
    document.getElementById('btnShowAll').addEventListener('click', selectAllRegions);

    // Region filter toggle
    elements.regionToggleBtn.addEventListener('click', () => {
        state.regionFilterCollapsed = !state.regionFilterCollapsed;
        elements.regionChips.classList.toggle('collapsed', state.regionFilterCollapsed);
        elements.regionToggleBtn.textContent = state.regionFilterCollapsed ? '펼치기' : '접기';
    });
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
    document.body.style.overflow = 'hidden';
}

/**
 * Close sidebar
 */
function closeSidebar() {
    elements.sidebar.classList.remove('open');
    elements.mobileToggle.classList.remove('active');
    elements.overlay.classList.remove('active');
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
