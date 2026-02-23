/**
 * 출퇴근 시간 등고선 맵 - 프론트엔드
 */

const COOKIE_COMMUTE = 'pins_commute';

// 색상 스케일: 녹색(~15분) → 노랑(~30분) → 주황(~60분) → 빨강(~90분)
const COMMUTE_COLOR_STOPS = [
    { min: 0, color: [34, 197, 94] },     // #22c55e 녹색
    { min: 15, color: [132, 204, 22] },    // #84cc16 연두
    { min: 30, color: [234, 179, 8] },     // #eab308 노랑
    { min: 45, color: [249, 115, 22] },    // #f97316 주황
    { min: 60, color: [239, 68, 68] },     // #ef4444 빨강
    { min: 90, color: [153, 27, 27] },     // #991b1b 진빨강
];

const commuteState = {
    enabled: false,
    meta: null,
    currentData: null,
    gridLayer: null,
    targetId: null,
    timeSlot: null,
    direction: 'morning', // 'morning' or 'evening'
    cache: {},            // 로드된 데이터 캐시
};

/**
 * 초기화
 */
async function initCommute() {
    // 메타데이터 로드
    try {
        const resp = await fetch('data/commute/meta.json');
        if (!resp.ok) return;
        commuteState.meta = await resp.json();
    } catch (e) {
        console.warn('출퇴근 메타데이터 로드 실패:', e);
        return;
    }

    // 쿠키에서 이전 상태 복원
    const saved = getCookie(COOKIE_COMMUTE);
    if (saved) {
        commuteState.enabled = saved.enabled || false;
        commuteState.targetId = saved.targetId || null;
        commuteState.timeSlot = saved.timeSlot || null;
        commuteState.direction = saved.direction || 'morning';
    }

    // 수집된 데이터가 있는 타겟만 추출
    const collected = commuteState.meta.collected || {};
    const availableTargetIds = Object.keys(collected).filter(id => collected[id].length > 0);

    // 기본값 설정 - 수집된 타겟 중에서 선택
    if (!commuteState.targetId || !availableTargetIds.includes(commuteState.targetId)) {
        commuteState.targetId = availableTargetIds[0] || null;
    }
    if (!commuteState.timeSlot && commuteState.targetId) {
        commuteState.timeSlot = collected[commuteState.targetId][0] || '0800';
    }

    // UI 생성
    buildCommuteUI();

    // 이전에 활성화 상태였으면 데이터 로드
    if (commuteState.enabled) {
        loadAndRenderCommute();
    }
}

/**
 * UI 패널 구성
 */
function buildCommuteUI() {
    const panel = document.getElementById('commutePanel');
    if (!panel || !commuteState.meta) return;

    const meta = commuteState.meta;
    const collected = meta.collected || {};

    // 수집된 타겟만 표시
    const availableTargets = meta.targets.filter(t => collected[t.id] && collected[t.id].length > 0);

    // 수집 데이터 없으면 패널 숨김
    if (availableTargets.length === 0) {
        panel.style.display = 'none';
        return;
    }

    // 현재 선택 타겟의 가용 슬롯
    const currentSlots = collected[commuteState.targetId] || [];
    const morningSlots = currentSlots.filter(s => parseInt(s) < 1200);
    const eveningSlots = currentSlots.filter(s => parseInt(s) >= 1200);

    // 방향에 맞는 슬롯 목록
    const displaySlots = commuteState.direction === 'morning' ? morningSlots : eveningSlots;

    // 선택된 시간이 현재 방향에 없으면 첫번째로 리셋
    if (displaySlots.length > 0 && !displaySlots.includes(commuteState.timeSlot)) {
        commuteState.timeSlot = displaySlots[0];
    }

    panel.innerHTML = `
        <div class="commute-section-title">출퇴근 시간</div>
        <div class="commute-toggle-row">
            <span class="commute-toggle-label">등고선 표시</span>
            <div class="commute-toggle ${commuteState.enabled ? 'active' : ''}" id="commuteToggle"></div>
        </div>
        <div class="commute-controls ${commuteState.enabled ? '' : 'hidden'}" id="commuteControls">
            <div class="commute-control-group">
                <span class="commute-control-label">목적지</span>
                <select class="commute-select" id="commuteTarget">
                    ${availableTargets.map(t =>
                        `<option value="${t.id}" ${t.id === commuteState.targetId ? 'selected' : ''}>${t.name}</option>`
                    ).join('')}
                </select>
            </div>
            <div class="commute-control-group">
                <span class="commute-control-label">방향</span>
                <div class="commute-direction-row">
                    <button class="commute-dir-btn ${commuteState.direction === 'morning' ? 'active' : ''}" data-dir="morning">출근 (TO)</button>
                    <button class="commute-dir-btn ${commuteState.direction === 'evening' ? 'active' : ''}" data-dir="evening">퇴근 (FROM)</button>
                </div>
            </div>
            <div class="commute-control-group">
                <span class="commute-control-label">시간대</span>
                <select class="commute-select" id="commuteTime">
                    ${displaySlots.map(s =>
                        `<option value="${s}" ${s === commuteState.timeSlot ? 'selected' : ''}>${formatSlot(s)}</option>`
                    ).join('')}
                </select>
            </div>
            <div class="commute-legend">
                <div class="commute-legend-bar"></div>
                <div class="commute-legend-labels">
                    <span>15분</span>
                    <span>30분</span>
                    <span>45분</span>
                    <span>60분</span>
                    <span>90분</span>
                </div>
            </div>
            <div class="commute-status" id="commuteStatus"></div>
        </div>
    `;

    // 이벤트 바인딩
    document.getElementById('commuteToggle').addEventListener('click', toggleCommute);

    document.getElementById('commuteTarget').addEventListener('change', (e) => {
        commuteState.targetId = e.target.value;
        saveCommuteState();
        // 방향/슬롯 UI 갱신
        buildCommuteUI();
        if (commuteState.enabled) loadAndRenderCommute();
    });

    document.getElementById('commuteTime').addEventListener('change', (e) => {
        commuteState.timeSlot = e.target.value;
        saveCommuteState();
        if (commuteState.enabled) loadAndRenderCommute();
    });

    panel.querySelectorAll('.commute-dir-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            commuteState.direction = btn.dataset.dir;
            saveCommuteState();
            buildCommuteUI();
            if (commuteState.enabled) loadAndRenderCommute();
        });
    });
}

/**
 * 시간 슬롯 포맷 (예: "0800" → "08:00")
 */
function formatSlot(slot) {
    return slot.substring(0, 2) + ':' + slot.substring(2);
}

/**
 * 토글 활성화/비활성화
 */
function toggleCommute() {
    commuteState.enabled = !commuteState.enabled;
    saveCommuteState();

    const toggle = document.getElementById('commuteToggle');
    const controls = document.getElementById('commuteControls');
    toggle.classList.toggle('active', commuteState.enabled);
    controls.classList.toggle('hidden', !commuteState.enabled);

    if (commuteState.enabled) {
        loadAndRenderCommute();
    } else {
        clearCommuteGrid();
    }
}

/**
 * 데이터 로드 & 렌더링
 */
async function loadAndRenderCommute() {
    const { targetId, timeSlot } = commuteState;
    if (!targetId || !timeSlot) return;

    const key = `${targetId}_car_${timeSlot}`;
    const statusEl = document.getElementById('commuteStatus');

    // 캐시 확인
    if (commuteState.cache[key]) {
        commuteState.currentData = commuteState.cache[key];
        renderCommuteGrid();
        return;
    }

    // 로드
    if (statusEl) {
        statusEl.textContent = '데이터 로딩 중...';
        statusEl.className = 'commute-status loading';
    }

    try {
        const resp = await fetch(`data/commute/${key}.json`);
        if (!resp.ok) {
            throw new Error(`데이터 없음 (${resp.status})`);
        }
        const data = await resp.json();
        commuteState.cache[key] = data;
        commuteState.currentData = data;

        if (statusEl) {
            statusEl.textContent = '';
            statusEl.className = 'commute-status';
        }

        renderCommuteGrid();
    } catch (e) {
        console.warn('출퇴근 데이터 로드 실패:', e);
        if (statusEl) {
            statusEl.textContent = '데이터를 찾을 수 없습니다';
            statusEl.className = 'commute-status error';
        }
        clearCommuteGrid();
    }
}

/**
 * 그리드 셀 렌더링
 */
function renderCommuteGrid() {
    clearCommuteGrid();

    const data = commuteState.currentData;
    if (!data || !data.grid || !data.data) return;

    const { origin_lat, origin_lng, step_lat, step_lng, rows, cols } = data.grid;
    const gridData = data.data;

    const layer = L.layerGroup();

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const val = gridData[r] && gridData[r][c];
            if (val === null || val === undefined) continue;

            const lat = origin_lat + r * step_lat;
            const lng = origin_lng + c * step_lng;

            const color = durationToColor(val);

            const bounds = [
                [lat - step_lat / 2, lng - step_lng / 2],
                [lat + step_lat / 2, lng + step_lng / 2],
            ];

            const rect = L.rectangle(bounds, {
                color: 'transparent',
                weight: 0,
                fillColor: color,
                fillOpacity: 0.45,
                interactive: true,
            });

            rect.bindTooltip(`${val}분`, {
                permanent: false,
                direction: 'top',
                className: 'commute-tooltip',
            });

            layer.addLayer(rect);
        }
    }

    layer.addTo(state.map);
    // 그리드를 마커 아래에 표시
    layer.eachLayer(l => {
        if (l.bringToBack) l.bringToBack();
    });

    commuteState.gridLayer = layer;
    state.commuteLayer = layer;
}

/**
 * 그리드 레이어 제거
 */
function clearCommuteGrid() {
    if (commuteState.gridLayer) {
        state.map.removeLayer(commuteState.gridLayer);
        commuteState.gridLayer = null;
        state.commuteLayer = null;
    }
}

/**
 * 소요시간 → 색상 변환 (선형 보간)
 */
function durationToColor(minutes) {
    const stops = COMMUTE_COLOR_STOPS;

    if (minutes <= stops[0].min) {
        const [r, g, b] = stops[0].color;
        return `rgb(${r},${g},${b})`;
    }

    for (let i = 1; i < stops.length; i++) {
        if (minutes <= stops[i].min) {
            const prev = stops[i - 1];
            const curr = stops[i];
            const t = (minutes - prev.min) / (curr.min - prev.min);

            const r = Math.round(prev.color[0] + t * (curr.color[0] - prev.color[0]));
            const g = Math.round(prev.color[1] + t * (curr.color[1] - prev.color[1]));
            const b = Math.round(prev.color[2] + t * (curr.color[2] - prev.color[2]));
            return `rgb(${r},${g},${b})`;
        }
    }

    // 초과
    const last = stops[stops.length - 1].color;
    return `rgb(${last[0]},${last[1]},${last[2]})`;
}

/**
 * 쿠키에 상태 저장
 */
function saveCommuteState() {
    setCookie(COOKIE_COMMUTE, {
        enabled: commuteState.enabled,
        targetId: commuteState.targetId,
        timeSlot: commuteState.timeSlot,
        direction: commuteState.direction,
    }, COOKIE_EXPIRY_DAYS);
}
