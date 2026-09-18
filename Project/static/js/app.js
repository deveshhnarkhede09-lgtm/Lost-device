/**
 * app.js - Client-Side Controller for Campus Lost & Found Intelligent Matching System
 * Connects frontend views with Flask REST APIs & CSE Matching Engine
 */

// Global State
let allItems = [];
let currentTypeFilter = "";
let currentSearchQuery = "";
let currentCategoryFilter = "";
let currentLocationFilter = "";

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

function initApp() {
  loadItems();
  loadStats();
  loadClaims();
  runSandboxMatching(); // Initialize sandbox with default scenario
}

// ---------------------------------------------------------
// Navigation & Tab Switching
// ---------------------------------------------------------

function switchTab(tabId) {
  // Update Nav items
  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
  });

  // Toggle Tab Panels
  document.querySelectorAll(".tab-panel").forEach(panel => {
    panel.classList.remove("active");
  });
  const targetPanel = document.getElementById(`tab-${tabId}`);
  if (targetPanel) {
    targetPanel.classList.add("active");
  }

  // Toggle Hero banner visibility (only visible on feed)
  const heroSection = document.getElementById("heroSection");
  if (heroSection) {
    heroSection.style.display = (tabId === "feed") ? "block" : "none";
  }

  // Refresh map pins if map tab opened
  if (tabId === "map") {
    renderCampusMapPins(allItems);
  }

  // Smooth scroll to top of content
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ---------------------------------------------------------
// Items API & Grid Rendering
// ---------------------------------------------------------

async function loadItems() {
  try {
    const res = await fetch("/api/items");
    const data = await res.json();
    if (data.success) {
      allItems = data.items;
      updateCounts(allItems);
      applyFilters();
      renderCampusMapPins(allItems);
    }
  } catch (err) {
    console.error("Failed to load items:", err);
    showToast("Error loading items from campus server", "danger");
  }
}

function updateCounts(items) {
  const countAll = items.length;
  const countLost = items.filter(i => i.type === "lost").length;
  const countFound = items.filter(i => i.type === "found").length;

  document.getElementById("countAll").textContent = countAll;
  document.getElementById("countLost").textContent = countLost;
  document.getElementById("countFound").textContent = countFound;

  document.getElementById("heroLostCount").textContent = countLost;
  document.getElementById("heroFoundCount").textContent = countFound;
}

function applyFilters() {
  let filtered = allItems.filter(item => {
    // Type filter
    if (currentTypeFilter && item.type !== currentTypeFilter) {
      return false;
    }

    // Category filter
    if (currentCategoryFilter && !item.category.toLowerCase().includes(currentCategoryFilter.toLowerCase())) {
      return false;
    }

    // Location filter
    if (currentLocationFilter && !item.location.toLowerCase().includes(currentLocationFilter.toLowerCase())) {
      return false;
    }

    // Search query filter
    if (currentSearchQuery) {
      const combined = `${item.title} ${item.category} ${item.brand} ${item.color} ${item.location} ${item.description} ${item.unique_marks}`.toLowerCase();
      if (!combined.includes(currentSearchQuery)) {
        return false;
      }
    }

    return true;
  });

  renderItemsGrid(filtered);
}

function renderItemsGrid(items) {
  const grid = document.getElementById("itemsGrid");
  const empty = document.getElementById("emptyState");
  const resultsCount = document.getElementById("resultsCount");

  resultsCount.textContent = `Showing ${items.length} item${items.length === 1 ? '' : 's'}`;

  if (items.length === 0) {
    grid.innerHTML = "";
    empty.style.display = "block";
    return;
  }

  empty.style.display = "none";
  grid.innerHTML = items.map(item => createItemCardHtml(item)).join("");
}

function createItemCardHtml(item) {
  const isLost = item.type === "lost";
  const badgeClass = isLost ? "type-lost-badge" : "type-found-badge";
  const typeIcon = isLost ? "fa-circle-exclamation" : "fa-hand-holding-heart";
  const typeText = isLost ? "Lost" : "Found";

  // Use image path or fallback SVG
  let imgSrc = item.image_path || "/static/images/items/id_card.svg";

  return `
    <div class="item-card" data-id="${item.id}">
      <div class="item-card-top">
        <span class="item-type-badge ${badgeClass}">
          <i class="fa-solid ${typeIcon}"></i> ${typeText}
        </span>
        <span class="item-status-pill">${item.status.toUpperCase()}</span>
        <img src="${imgSrc}" alt="${item.title}" class="item-card-image" onerror="this.src='/static/images/items/id_card.svg'">
      </div>

      <div class="item-card-body">
        <h3 class="item-card-title">${escapeHtml(item.title)}</h3>
        
        <div class="item-meta-tags">
          <span class="meta-tag"><i class="fa-solid fa-layer-group"></i> ${escapeHtml(item.category)}</span>
          ${item.brand ? `<span class="meta-tag"><i class="fa-solid fa-tag"></i> ${escapeHtml(item.brand)}</span>` : ''}
          ${item.color ? `<span class="meta-tag"><i class="fa-solid fa-palette"></i> ${escapeHtml(item.color)}</span>` : ''}
          <span class="meta-tag"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(item.location)}</span>
          <span class="meta-tag"><i class="fa-solid fa-calendar"></i> ${escapeHtml(item.date_lost_found)}</span>
        </div>

        <p class="item-card-desc">${escapeHtml(item.description || 'No description provided.')}</p>

        ${item.unique_marks ? `
          <div class="item-unique-mark-pill" title="Identifying mark">
            <i class="fa-solid fa-fingerprint"></i>
            <span>${escapeHtml(item.unique_marks)}</span>
          </div>
        ` : ''}

        <div class="item-card-footer">
          <button class="btn btn-match-scan btn-sm" onclick="inspectItemMatches(${item.id})">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Check Matches
          </button>
          ${!isLost && item.status !== 'resolved' ? `
            <button class="btn btn-outline btn-sm" onclick="openClaimModal(${item.id})">
              <i class="fa-solid fa-key"></i> Claim
            </button>
          ` : ''}
        </div>
      </div>
    </div>
  `;
}

// ---------------------------------------------------------
// Filter Handlers
// ---------------------------------------------------------

function setTypeFilter(type) {
  currentTypeFilter = type;
  document.querySelectorAll(".type-pill-group .pill-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-type") === type);
  });
  applyFilters();
}

function handleSearch(query) {
  currentSearchQuery = query.trim().toLowerCase();
  const clearBtn = document.getElementById("searchClearBtn");
  clearBtn.style.display = currentSearchQuery ? "block" : "none";
  applyFilters();
}

function clearSearch() {
  document.getElementById("searchInput").value = "";
  handleSearch("");
}

function handleCategoryFilter(val) {
  currentCategoryFilter = val;
  applyFilters();
}

function handleLocationFilter(val) {
  currentLocationFilter = val;
  applyFilters();
}

function resetFilters() {
  currentTypeFilter = "";
  currentSearchQuery = "";
  currentCategoryFilter = "";
  currentLocationFilter = "";

  document.getElementById("searchInput").value = "";
  document.getElementById("searchClearBtn").style.display = "none";
  document.getElementById("categorySelect").value = "";
  document.getElementById("locationSelect").value = "";

  document.querySelectorAll(".type-pill-group .pill-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-type") === "");
  });

  applyFilters();
}

// ---------------------------------------------------------
// Match Inspection Modal & Breakdown Analysis
// ---------------------------------------------------------

async function inspectItemMatches(itemId) {
  try {
    const res = await fetch(`/api/matches/${itemId}`);
    const data = await res.json();
    if (!data.success) return;

    const modalBody = document.getElementById("matchModalBody");
    const targetItem = allItems.find(i => i.id === itemId);

    if (!data.matches || data.matches.length === 0) {
      modalBody.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
          <h3>No Possible Matches Found Yet</h3>
          <p>Our algorithm hasn't detected a report meeting the similarity threshold for <strong>${escapeHtml(targetItem.title)}</strong>.</p>
          <p class="text-muted" style="font-size:0.85rem; margin-top:8px;">You will be automatically notified as soon as a matching report is submitted.</p>
        </div>
      `;
      openModal("matchModal");
      return;
    }

    // Render matches list with factor breakdowns
    modalBody.innerHTML = `
      <div style="margin-bottom: 20px;">
        <span class="badge badge-cse"><i class="fa-solid fa-microchip"></i> CSE Multi-Factor Similarity</span>
        <h3 style="font-family:var(--font-heading); margin-top:6px;">
          Comparing: <span style="color:#38bdf8;">${escapeHtml(targetItem.title)}</span> (${targetItem.type.toUpperCase()})
        </h3>
        <p class="text-muted" style="font-size:0.88rem;">Found ${data.matches.length} candidate report${data.matches.length > 1 ? 's' : ''} ranked by similarity score.</p>
      </div>

      <div class="matches-list" style="display:flex; flex-direction:column; gap:24px;">
        ${data.matches.map((m, idx) => renderMatchCardHtml(targetItem, m, idx)).join("")}
      </div>
    `;

    openModal("matchModal");
  } catch (err) {
    console.error("Failed to inspect matches:", err);
    showToast("Error computing matches", "danger");
  }
}

function renderMatchCardHtml(targetItem, match, index) {
  const cand = match.matched_item;
  const score = match.score;
  const confBadge = score >= 75 ? 'badge-high' : (score >= 50 ? 'badge-medium' : 'badge-low');

  // Determine which is lost and which is found
  const lostItem = targetItem.type === "lost" ? targetItem : cand;
  const foundItem = targetItem.type === "found" ? targetItem : cand;

  return `
    <div class="match-candidate-card" style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:var(--radius-lg); padding:20px;">
      
      <!-- Top Match Banner -->
      <div class="score-summary-banner" style="margin-bottom:16px;">
        <div class="score-ring-wrap">
          <div class="score-circle" style="border-color:${score >= 75 ? '#10b981' : (score >= 50 ? '#f59e0b' : '#ef4444')};">
            <span class="score-number">${score}</span>
            <span class="score-unit">/100</span>
          </div>
        </div>
        <div class="score-banner-text">
          <div class="score-status-row">
            <span class="badge ${confBadge}">${match.confidence} CONFIDENCE</span>
            <span class="score-status-title">${match.status_text}</span>
          </div>
          <p class="score-explanation">
            Candidate: <strong>${escapeHtml(cand.title)}</strong> (${cand.type.toUpperCase()}) &bull; Reported at <strong>${escapeHtml(cand.location)}</strong> on <strong>${escapeHtml(cand.date_lost_found)}</strong>
          </p>
        </div>
      </div>

      <!-- Side-by-side comparison -->
      <div class="match-comparison-row">
        <div class="comparison-card">
          <h4 style="color:#f87171;"><i class="fa-solid fa-circle-exclamation"></i> Lost Report: ${escapeHtml(lostItem.title)}</h4>
          <p style="font-size:0.85rem; color:var(--text-muted);">${escapeHtml(lostItem.description)}</p>
          <div style="font-size:0.75rem; margin-top:6px; color:#fbbf24;">Mark: ${escapeHtml(lostItem.unique_marks || 'None')}</div>
        </div>
        <div class="comparison-card">
          <h4 style="color:#34d399;"><i class="fa-solid fa-hand-holding-heart"></i> Found Report: ${escapeHtml(foundItem.title)}</h4>
          <p style="font-size:0.85rem; color:var(--text-muted);">${escapeHtml(foundItem.description)}</p>
          <div style="font-size:0.75rem; margin-top:6px; color:#fbbf24;">Mark: ${escapeHtml(foundItem.unique_marks || 'None')}</div>
        </div>
      </div>

      <!-- Factor breakdown table -->
      <div class="factor-matrix-card" style="margin-top:14px;">
        <h4 style="font-size:0.95rem; font-weight:700; margin-bottom:12px;"><i class="fa-solid fa-calculator"></i> Factor Score Breakdown</h4>
        <div class="factor-table-wrap">
          <table class="factor-table">
            <thead>
              <tr>
                <th>Factor</th>
                <th>Weight</th>
                <th>Score</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              ${Object.entries(match.breakdown).map(([key, f]) => `
                <tr>
                  <td><strong>${escapeHtml(f.label)}</strong></td>
                  <td>${f.max} pts</td>
                  <td class="factor-score-cell">${f.score}/${f.max}</td>
                  <td style="color:var(--text-muted); font-size:0.82rem;">${escapeHtml(f.reason)}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action Button -->
      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:16px;">
        <button class="btn btn-success btn-sm" onclick="openClaimModalFromMatch(${foundItem.id}, ${lostItem.id}, ${score})">
          <i class="fa-solid fa-shield-halved"></i> Claim & Unlock Contact
        </button>
      </div>
    </div>
  `;
}

function openDemoMatch(lostId, foundId) {
  inspectItemMatches(lostId);
}

// ---------------------------------------------------------
// Privacy Verification & Claim Modal
// ---------------------------------------------------------

async function openClaimModal(foundItemId) {
  try {
    const res = await fetch(`/api/items/${foundItemId}`);
    const data = await res.json();
    if (!data.success) return;

    const item = data.item;
    document.getElementById("claimFoundItemId").value = item.id;
    document.getElementById("claimLostItemId").value = "";
    document.getElementById("claimMatchScore").value = 90;

    document.getElementById("claimItemSummary").innerHTML = `
      <div style="display:flex; align-items:center; gap:14px; background:rgba(255,255,255,0.04); padding:12px; border-radius:var(--radius-md);">
        <img src="${item.image_path || '/static/images/items/id_card.svg'}" style="width:48px; height:48px; object-fit:contain;">
        <div>
          <h4 style="font-size:1rem; font-weight:700;">${escapeHtml(item.title)}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(item.location)} &bull; ${escapeHtml(item.category)}</span>
        </div>
      </div>
    `;

    const qText = item.verification_question || "What secret identifying mark or color detail is on this item?";
    document.getElementById("claimQuestionText").textContent = `"${qText}"`;
    document.getElementById("claimAnswerInput").value = "";
    document.getElementById("claimResultBox").style.display = "none";
    document.getElementById("claimSubmitBtn").style.display = "inline-flex";

    openModal("claimModal");
  } catch (err) {
    console.error("Error opening claim modal:", err);
  }
}

function openClaimModalFromMatch(foundId, lostId, score) {
  closeModal("matchModal");
  openClaimModal(foundId);
  document.getElementById("claimLostItemId").value = lostId;
  document.getElementById("claimMatchScore").value = score;
}

async function handleClaimSubmit(e) {
  e.preventDefault();

  const foundId = document.getElementById("claimFoundItemId").value;
  const lostId = document.getElementById("claimLostItemId").value;
  const matchScore = parseInt(document.getElementById("claimMatchScore").value) || 90;
  const claimantAnswer = document.getElementById("claimAnswerInput").value.trim();
  const claimantName = document.getElementById("claimantName").value.trim();
  const claimantEmail = document.getElementById("claimantEmail").value.trim();
  const claimantPhone = document.getElementById("claimantPhone").value.trim();

  const payload = {
    found_item_id: parseInt(foundId),
    lost_item_id: lostId ? parseInt(lostId) : null,
    claimant_name: claimantName,
    claimant_email: claimantEmail,
    claimant_phone: claimantPhone,
    claimant_answer: claimantAnswer,
    match_score: matchScore
  };

  try {
    const res = await fetch("/api/claims", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    const resultBox = document.getElementById("claimResultBox");
    resultBox.style.display = "block";

    if (data.is_verified) {
      resultBox.innerHTML = `
        <div style="color:#34d399; margin-bottom:12px;">
          <i class="fa-solid fa-circle-check" style="font-size:1.4rem;"></i>
          <strong style="margin-left:8px; font-size:1.1rem;">Verification Successful!</strong>
          <p style="margin-top:6px; color:#cbd5e1; font-size:0.88rem;">${data.message}</p>
        </div>
        <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:var(--radius-sm); font-size:0.88rem;">
          <div><strong>Finder / Custodian:</strong> ${escapeHtml(data.contact_info.name)}</div>
          <div><strong>Campus Email:</strong> <a href="mailto:${data.contact_info.email}" style="color:#38bdf8;">${escapeHtml(data.contact_info.email)}</a></div>
          <div><strong>Phone:</strong> ${escapeHtml(data.contact_info.phone || 'N/A')}</div>
          <div><strong>Location for pickup:</strong> ${escapeHtml(data.contact_info.location)}</div>
        </div>
      `;
      document.getElementById("claimSubmitBtn").style.display = "none";
      loadItems();
      loadStats();
      loadClaims();
      showToast("Ownership verified! Contact unlocked.", "success");
    } else {
      resultBox.innerHTML = `
        <div style="color:#fbbf24;">
          <i class="fa-solid fa-clock" style="font-size:1.4rem;"></i>
          <strong style="margin-left:8px; font-size:1.05rem;">Claim Registered for Manual Review</strong>
          <p style="margin-top:6px; color:#cbd5e1; font-size:0.85rem;">
            ${data.message} The finder or campus security desk has received your answer and will contact you at <strong>${escapeHtml(claimantEmail)}</strong>.
          </p>
        </div>
      `;
      loadClaims();
    }
  } catch (err) {
    console.error("Error submitting claim:", err);
    showToast("Error processing verification", "danger");
  }
}

// ---------------------------------------------------------
// Report Lost / Found Modals & Form Submission
// ---------------------------------------------------------

function openReportModal(type) {
  const modal = document.getElementById("reportModal");
  const modalTitle = document.getElementById("reportModalTitle");
  const modalIcon = document.getElementById("reportModalIcon");
  const reportTypeInput = document.getElementById("reportType");
  const privacySection = document.getElementById("privacyQuestionSection");

  reportTypeInput.value = type;

  // Set today's date as default
  const todayStr = new Date().toISOString().split("T")[0];
  document.getElementById("formDate").value = todayStr;

  if (type === "lost") {
    modalTitle.textContent = "Report Lost Item";
    modalIcon.className = "fa-solid fa-circle-exclamation text-danger";
    privacySection.style.display = "none";
  } else {
    modalTitle.textContent = "Report Found Item";
    modalIcon.className = "fa-solid fa-hand-holding-heart text-success";
    privacySection.style.display = "block";
  }

  openModal("reportModal");
}

async function handleReportSubmit(e) {
  e.preventDefault();
  const form = document.getElementById("reportForm");
  const formData = new FormData(form);

  const submitBtn = document.getElementById("reportSubmitBtn");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Scanning for matches...`;

  try {
    const res = await fetch("/api/items", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit & Scan For Matches`;

    if (!data.success) {
      showToast(data.error || "Failed to submit report", "danger");
      return;
    }

    closeModal("reportModal");
    form.reset();
    showToast(data.message, "success");
    loadItems();
    loadStats();

    // Check if an instant high-confidence match was discovered!
    if (data.has_top_match && data.top_match) {
      triggerInstantMatchAlert(data.item_id, data.top_match);
    }
  } catch (err) {
    console.error("Error submitting report:", err);
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit & Scan For Matches`;
    showToast("Network error submitting report", "danger");
  }
}

function triggerInstantMatchAlert(newItemId, topMatch) {
  const modalBody = document.getElementById("instantMatchModalBody");
  const cand = topMatch.matched_item;
  const score = topMatch.score;

  modalBody.innerHTML = `
    <div class="score-summary-banner" style="margin-bottom:18px;">
      <div class="score-ring-wrap">
        <div class="score-circle" style="border-color:#10b981;">
          <span class="score-number">${score}</span>
          <span class="score-unit">/100</span>
        </div>
      </div>
      <div class="score-banner-text">
        <div class="score-status-row">
          <span class="badge badge-high">${topMatch.confidence} CONFIDENCE</span>
          <span class="score-status-title">Match Found Immediately!</span>
        </div>
        <p class="score-explanation">
          Your report directly correlates with an existing report: <strong>${escapeHtml(cand.title)}</strong> at <strong>${escapeHtml(cand.location)}</strong>.
        </p>
      </div>
    </div>

    <div style="display:flex; justify-content:flex-end; gap:12px;">
      <button class="btn btn-ghost" onclick="closeModal('instantMatchModal')">Dismiss</button>
      <button class="btn btn-primary" onclick="closeModal('instantMatchModal'); inspectItemMatches(${newItemId});">
        <i class="fa-solid fa-wand-magic-sparkles"></i> View Match Analysis
      </button>
    </div>
  `;

  openModal("instantMatchModal");
}

// ---------------------------------------------------------
// Interactive Campus Map Pin Rendering
// ---------------------------------------------------------

const LOCATION_COORDINATES = {
  // Academic & Auditoriums
  "AB1 Hall": { x: 195, y: 110 },
  "AB1": { x: 195, y: 110 },
  "Academic Block 1": { x: 195, y: 110 },
  "Academic Block (AB)": { x: 195, y: 110 },
  "AB2": { x: 325, y: 110 },
  "Academic Block 2": { x: 325, y: 110 },
  "MPH": { x: 212, y: 205 },
  "Multipurpose Hall": { x: 212, y: 205 },
  "Open Audi": { x: 337, y: 205 },
  "Open Auditorium": { x: 337, y: 205 },
  "Central Library": { x: 260, y: 80 },
  "Library": { x: 260, y: 80 },

  // Healthcare & Gates
  "Hospital": { x: 140, y: 355 },
  "Health Centre": { x: 140, y: 355 },
  "Parking Gate / Parcel Point": { x: 295, y: 400 },
  "Parking Gate": { x: 295, y: 400 },
  "Parcel Point": { x: 295, y: 400 },
  "Main Gate of Entrance": { x: 470, y: 400 },
  "Main Gate of Entrence": { x: 470, y: 400 },
  "Main Gate": { x: 470, y: 400 },

  // Boys Hostels (BH 1-6, 7A, 7B, 8A, 8B)
  "Boys Hostel 1": { x: 440, y: 105 },
  "Boys Hostel 2": { x: 462, y: 105 },
  "Boys Hostel 3": { x: 485, y: 105 },
  "Boys Hostel 4": { x: 560, y: 105 },
  "Boys Hostel 5": { x: 582, y: 105 },
  "Boys Hostel 6": { x: 605, y: 105 },
  "Boys Hostel 7A": { x: 445, y: 190 },
  "Boys Hostel 7B": { x: 475, y: 190 },
  "Boys Hostel 8A": { x: 565, y: 190 },
  "Boys Hostel 8B": { x: 595, y: 190 },
  "Boys Hostel": { x: 500, y: 150 },

  // Girls Hostels (GH 1, GH 2, Block A, Block B)
  "Girls Hostel 1": { x: 70, y: 105 },
  "Girls Hostel 2": { x: 70, y: 130 },
  "Girls Hostel Block A": { x: 70, y: 195 },
  "Girls Hostel Block B": { x: 70, y: 225 },
  "Girls Hostel": { x: 70, y: 160 },

  // Student Hub & Grounds
  "Underbelly Food Court": { x: 270, y: 300 },
  "Underbelly": { x: 270, y: 300 },
  "Sports Arena": { x: 70, y: 400 },
  "Campus Grounds": { x: 280, y: 220 }
};

function renderCampusMapPins(items) {
  const layer = document.getElementById("mapPinsLayer");
  if (!layer) return;

  // Group items by approximate location to spread overlapping pins
  const pinMarkup = items.map((item, idx) => {
    let locKey = Object.keys(LOCATION_COORDINATES).find(k => item.location.toLowerCase().includes(k.toLowerCase())) || "Campus Grounds";
    let base = LOCATION_COORDINATES[locKey] || { x: 270, y: 250 };

    // Jitter coordinates slightly so multiple items don't overlap completely
    const jitterX = ((idx % 4) - 1.5) * 16;
    const jitterY = (Math.floor(idx / 4) % 3 - 1) * 14;
    const x = base.x + jitterX;
    const y = base.y + jitterY;

    const isLost = item.type === "lost";
    const color = isLost ? "#ef4444" : "#10b981";

    return `
      <g class="map-pin" data-id="${item.id}" onclick="selectMapPin(${item.id})">
        <circle cx="${x}" cy="${y}" r="11" fill="${color}" stroke="#ffffff" stroke-width="2.5" filter="url(#pinShadow)"/>
        <text x="${x}" y="${y + 4}" fill="#ffffff" font-family="Outfit" font-size="10" font-weight="bold" text-anchor="middle">
          ${isLost ? '!' : '✓'}
        </text>
      </g>
    `;
  }).join("");

  layer.innerHTML = pinMarkup;
}

function selectMapPin(itemId) {
  const item = allItems.find(i => i.id === itemId);
  if (!item) return;

  const sidebar = document.getElementById("mapSidebarContent");
  const isLost = item.type === "lost";

  sidebar.innerHTML = `
    <div style="text-align:center; margin-bottom:16px;">
      <span class="item-type-badge ${isLost ? 'type-lost-badge' : 'type-found-badge'}" style="position:static; display:inline-flex;">
        ${item.type.toUpperCase()}
      </span>
      <h4 style="font-family:var(--font-heading); font-size:1.2rem; font-weight:800; margin-top:8px; color:#ffffff;">
        ${escapeHtml(item.title)}
      </h4>
      <div style="background:rgba(56, 189, 248, 0.15); border:1px solid rgba(56, 189, 248, 0.4); color:#38bdf8; padding:6px 14px; border-radius:var(--radius-full); font-size:0.85rem; font-weight:700; display:inline-flex; align-items:center; gap:6px; margin:8px auto 4px;">
        <i class="fa-solid fa-location-dot"></i> ${escapeHtml(item.location)}
      </div>
    </div>

    <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); padding:14px; border-radius:var(--radius-md); font-size:0.88rem; margin-bottom:16px;">
      <div style="margin-bottom:4px;"><strong>Category:</strong> <span style="color:#cbd5e1;">${escapeHtml(item.category)}</span></div>
      <div style="margin-bottom:4px;"><strong>Brand:</strong> <span style="color:#cbd5e1;">${escapeHtml(item.brand || 'N/A')}</span></div>
      <div style="margin-bottom:4px;"><strong>Color:</strong> <span style="color:#cbd5e1;">${escapeHtml(item.color || 'N/A')}</span></div>
      <div style="margin-bottom:4px;"><strong>Date:</strong> <span style="color:#cbd5e1;">${escapeHtml(item.date_lost_found)}</span></div>
      ${item.unique_marks ? `<div style="color:#fbbf24; margin-top:6px; padding-top:6px; border-top:1px dashed rgba(255,255,255,0.1);"><strong>Identifying Mark:</strong> ${escapeHtml(item.unique_marks)}</div>` : ''}
    </div>

    <p style="font-size:0.84rem; color:var(--text-muted); line-height:1.5; margin-bottom:16px;">
      ${escapeHtml(item.description)}
    </p>

    <button class="btn btn-match-scan btn-sm" style="width:100%;" onclick="inspectItemMatches(${item.id})">
      <i class="fa-solid fa-wand-magic-sparkles"></i> Check Matches for this Item
    </button>
  `;
}

function filterMapByLocation(locName) {
  const sidebar = document.getElementById("mapSidebarContent");
  const matchingItems = allItems.filter(i => i.location.toLowerCase().includes(locName.toLowerCase()));

  sidebar.innerHTML = `
    <div style="background:rgba(56, 189, 248, 0.12); border:1px solid rgba(56, 189, 248, 0.4); border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
      <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.5px; color:#38bdf8; font-weight:700;">
        <i class="fa-solid fa-building-columns"></i> VIT Bhopal Location Selected
      </div>
      <h3 style="font-family:var(--font-heading); font-size:1.25rem; font-weight:800; color:#ffffff; margin-top:4px;">
        ${escapeHtml(locName)}
      </h3>
      <p style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">
        ${matchingItems.length} active report${matchingItems.length === 1 ? '' : 's'} at this building.
      </p>
    </div>

    ${matchingItems.length > 0 ? `
      <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:16px; max-height:260px; overflow-y:auto;">
        ${matchingItems.map(item => `
          <div onclick="selectMapPin(${item.id})" style="background:rgba(255, 255, 255, 0.04); border:1px solid var(--border-color); padding:10px; border-radius:var(--radius-sm); cursor:pointer; transition:all 0.2s ease;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="font-size:0.9rem; color:#f8fafc;">${escapeHtml(item.title)}</strong>
              <span class="badge ${item.type === 'lost' ? 'badge-low' : 'badge-high'}" style="font-size:0.68rem; padding:2px 8px;">
                ${item.type.toUpperCase()}
              </span>
            </div>
            <div style="font-size:0.75rem; color:var(--text-dim); margin-top:4px;">
              ${escapeHtml(item.category)} &bull; ${escapeHtml(item.date_lost_found)}
            </div>
          </div>
        `).join("")}
      </div>
    ` : `
      <div style="text-align:center; padding:24px 10px; color:var(--text-muted); font-size:0.85rem;">
        <i class="fa-solid fa-circle-check text-success" style="font-size:1.8rem; display:block; margin-bottom:8px;"></i>
        No active lost or found reports currently recorded at this building.
      </div>
    `}

    <button class="btn btn-outline btn-sm" style="width:100%;" onclick="goToFeedFiltered('${escapeHtml(locName)}')">
      <i class="fa-solid fa-list-ul"></i> View in Items Feed
    </button>
  `;
}

function goToFeedFiltered(locName) {
  currentLocationFilter = locName;
  const select = document.getElementById("locationSelect");
  if (select) select.value = locName;
  switchTab("feed");
  applyFilters();
}

// ---------------------------------------------------------
// CSE Algorithm Lab / Sandbox
// ---------------------------------------------------------

const SCENARIOS = {
  "laptop_bag": {
    lost: {
      title: "Black HP laptop bag",
      category: "laptop bag",
      brand: "HP",
      color: "black",
      location: "Library",
      date_lost_found: "2026-09-17",
      time_lost_found: "14:00",
      description: "Lost my black HP laptop bag near the library reading section.",
      unique_marks: "Small red keychain on the zipper"
    },
    found: {
      title: "Black laptop bag",
      category: "laptop bag",
      brand: "HP",
      color: "black",
      location: "Central Library",
      date_lost_found: "2026-09-17",
      time_lost_found: "14:30",
      description: "Found a black HP laptop bag on a bench near Central Library.",
      unique_marks: "Red tag or keychain attached"
    }
  },
  "hp_laptop": {
    lost: {
      title: "Silver HP Laptop",
      category: "laptop",
      brand: "HP",
      color: "silver",
      location: "Library",
      date_lost_found: "2026-09-17",
      time_lost_found: "11:00",
      description: "Silver HP laptop left at 2nd floor desk. Urgent, contains final project!",
      unique_marks: "Sticker near keyboard"
    },
    found: {
      title: "HP silver laptop",
      category: "laptop",
      brand: "HP",
      color: "silver",
      location: "Library",
      date_lost_found: "2026-09-17",
      time_lost_found: "11:45",
      description: "Found an HP silver laptop in library. Small sticker visible.",
      unique_marks: "Small sticker near keyboard"
    }
  },
  "airpods": {
    lost: {
      title: "Apple AirPods Pro",
      category: "earphones",
      brand: "Apple",
      color: "white",
      location: "Student Cafeteria",
      date_lost_found: "2026-09-18",
      time_lost_found: "12:30",
      description: "White AirPods Pro in charging case left on cafeteria table near smoothie counter.",
      unique_marks: "Astronaut silicone sleeve cover"
    },
    found: {
      title: "White Wireless Earbuds Case",
      category: "earphones",
      brand: "Apple",
      color: "white",
      location: "Student Cafeteria",
      date_lost_found: "2026-09-18",
      time_lost_found: "13:00",
      description: "White Apple AirPods charging case found under table 14 in cafeteria.",
      unique_marks: "Blue silicone cover with astronaut graphic"
    }
  },
  "calculator": {
    lost: {
      title: "Casio FX-991CW Calculator",
      category: "calculator",
      brand: "Casio",
      color: "black",
      location: "Block A - Academic",
      date_lost_found: "2026-09-16",
      time_lost_found: "15:00",
      description: "Scientific calculator left behind in Room 304 after Engineering Mathematics lecture.",
      unique_marks: "Initials RN marked on battery cover"
    },
    found: {
      title: "Casio Scientific Calculator",
      category: "calculator",
      brand: "Casio",
      color: "black",
      location: "Block A - Academic",
      date_lost_found: "2026-09-16",
      time_lost_found: "15:45",
      description: "Black Casio calculator discovered on podium in Block A Room 304.",
      unique_marks: "Handwritten initials on battery cover"
    }
  },
  "id_card": {
    lost: {
      title: "VIT Bhopal Student ID Card",
      category: "id card",
      brand: "VIT Bhopal",
      color: "blue and white",
      location: "Multipurpose Hall (MPH)",
      date_lost_found: "2026-09-18",
      time_lost_found: "10:00",
      description: "Student ID card lost during morning orientation in Multipurpose Hall.",
      unique_marks: "Blue lanyard with registration number 22BCE10045"
    },
    found: {
      title: "Found Student ID Card with Blue Lanyard",
      category: "id card",
      brand: "VIT Bhopal",
      color: "blue and white",
      location: "Multipurpose Hall (MPH)",
      date_lost_found: "2026-09-18",
      time_lost_found: "10:45",
      description: "Found a student ID card on row 12 chair in Multipurpose Hall auditorium.",
      unique_marks: "Blue lanyard with registration number ending in 10045"
    }
  },
  "mismatch": {
    lost: {
      title: "MacBook Air",
      category: "laptop",
      brand: "Apple",
      color: "silver",
      location: "Library",
      date_lost_found: "2026-09-17",
      time_lost_found: "14:00",
      description: "Lost laptop in reading section",
      unique_marks: ""
    },
    found: {
      title: "Blue Hydro Flask bottle",
      category: "water bottle",
      brand: "Hydro Flask",
      color: "blue",
      location: "Sports Complex",
      date_lost_found: "2026-09-02",
      time_lost_found: "09:00",
      description: "Found bottle near badminton court",
      unique_marks: ""
    }
  }
};

function loadSandboxScenario(key) {
  const scenario = SCENARIOS[key];
  if (!scenario) return;

  document.getElementById("sbLostTitle").value = scenario.lost.title;
  document.getElementById("sbLostCategory").value = scenario.lost.category;
  document.getElementById("sbLostBrand").value = scenario.lost.brand;
  document.getElementById("sbLostColor").value = scenario.lost.color;
  document.getElementById("sbLostLocation").value = scenario.lost.location;
  document.getElementById("sbLostDate").value = scenario.lost.date_lost_found;
  document.getElementById("sbLostTime").value = scenario.lost.time_lost_found;
  document.getElementById("sbLostDesc").value = scenario.lost.description;
  document.getElementById("sbLostMark").value = scenario.lost.unique_marks;

  document.getElementById("sbFoundTitle").value = scenario.found.title;
  document.getElementById("sbFoundCategory").value = scenario.found.category;
  document.getElementById("sbFoundBrand").value = scenario.found.brand;
  document.getElementById("sbFoundColor").value = scenario.found.color;
  document.getElementById("sbFoundLocation").value = scenario.found.location;
  document.getElementById("sbFoundDate").value = scenario.found.date_lost_found;
  document.getElementById("sbFoundTime").value = scenario.found.time_lost_found;
  document.getElementById("sbFoundDesc").value = scenario.found.description;
  document.getElementById("sbFoundMark").value = scenario.found.unique_marks;

  runSandboxMatching();
}

async function runSandboxMatching() {
  const lostItem = {
    title: document.getElementById("sbLostTitle").value,
    category: document.getElementById("sbLostCategory").value,
    brand: document.getElementById("sbLostBrand").value,
    color: document.getElementById("sbLostColor").value,
    location: document.getElementById("sbLostLocation").value,
    date_lost_found: document.getElementById("sbLostDate").value,
    time_lost_found: document.getElementById("sbLostTime").value,
    description: document.getElementById("sbLostDesc").value,
    unique_marks: document.getElementById("sbLostMark").value
  };

  const foundItem = {
    title: document.getElementById("sbFoundTitle").value,
    category: document.getElementById("sbFoundCategory").value,
    brand: document.getElementById("sbFoundBrand").value,
    color: document.getElementById("sbFoundColor").value,
    location: document.getElementById("sbFoundLocation").value,
    date_lost_found: document.getElementById("sbFoundDate").value,
    time_lost_found: document.getElementById("sbFoundTime").value,
    description: document.getElementById("sbFoundDesc").value,
    unique_marks: document.getElementById("sbFoundMark").value
  };

  try {
    const res = await fetch("/api/test-match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lost_item: lostItem, found_item: foundItem })
    });

    const data = await res.json();
    if (!data.success) return;

    const result = data.result;
    renderSandboxResults(result);
  } catch (err) {
    console.error("Sandbox evaluation error:", err);
  }
}

function renderSandboxResults(result) {
  const score = result.total_score;
  const scoreNum = document.getElementById("sbScoreNum");
  const scoreCircle = document.getElementById("sbScoreCircle");
  const confBadge = document.getElementById("sbConfidenceBadge");
  const statusTitle = document.getElementById("sbStatusTitle");
  const scoreDesc = document.getElementById("sbScoreDesc");

  scoreNum.textContent = score;

  const color = score >= 75 ? '#10b981' : (score >= 50 ? '#f59e0b' : '#ef4444');
  scoreCircle.style.borderColor = color;

  confBadge.textContent = `${result.confidence} CONFIDENCE`;
  confBadge.className = `badge ${score >= 75 ? 'badge-high' : (score >= 50 ? 'badge-medium' : 'badge-low')}`;

  statusTitle.textContent = result.status_text;
  scoreDesc.textContent = `The matching engine calculated a ${score}% composite similarity across all 7 weighted heuristic dimensions.`;

  const tbody = document.getElementById("sbBreakdownTbody");
  tbody.innerHTML = Object.entries(result.breakdown).map(([k, f]) => `
    <tr>
      <td><strong>${escapeHtml(f.label)}</strong></td>
      <td>${f.max} pts</td>
      <td class="factor-score-cell">${f.score}/${f.max}</td>
      <td style="color:var(--text-muted); font-size:0.85rem;">${escapeHtml(f.reason)}</td>
    </tr>
  `).join("");
}

// ---------------------------------------------------------
// Dashboard & Stats
// ---------------------------------------------------------

async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    if (!data.success) return;

    const s = data.stats;
    document.getElementById("dbLostCount").textContent = s.lost_count;
    document.getElementById("dbFoundCount").textContent = s.found_count;
    document.getElementById("dbResolvedCount").textContent = s.resolved_count;
  } catch (err) {
    console.error("Error loading stats:", err);
  }
}

async function loadClaims() {
  try {
    const res = await fetch("/api/claims");
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("claimsTbody");
    if (!data.claims || data.claims.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No ownership claims submitted yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.claims.map(c => `
      <tr>
        <td>#${c.id}</td>
        <td><strong>${escapeHtml(c.found_title || 'Item')}</strong></td>
        <td>${escapeHtml(c.claimant_name)}<br><span style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(c.claimant_email)}</span></td>
        <td style="color:#fbbf24;">"${escapeHtml(c.claimant_answer)}"</td>
        <td><strong style="color:#38bdf8;">${c.match_score}%</strong></td>
        <td><span class="badge ${c.status === 'approved' ? 'badge-approved' : 'badge-pending'}">${c.status.toUpperCase()}</span></td>
        <td>
          ${c.status === 'pending' ? `
            <button class="btn btn-xs btn-success" onclick="resolveClaim(${c.id}, 'approved')">Approve</button>
          ` : `<span style="color:#34d399; font-size:0.8rem;">✓ Resolved</span>`}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error loading claims:", err);
  }
}

async function resolveClaim(claimId, decision) {
  try {
    const res = await fetch(`/api/claims/${claimId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Claim marked as ${decision}`, "success");
      loadClaims();
      loadItems();
      loadStats();
    }
  } catch (err) {
    console.error("Error resolving claim:", err);
  }
}

// ---------------------------------------------------------
// Modal Helpers & Utility Functions
// ---------------------------------------------------------

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add("active");
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove("active");
}

function closeModalOnBackdrop(e, id) {
  if (e.target.id === id) {
    closeModal(id);
  }
}

function showToast(msg, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${type === 'success' ? 'fa-circle-check text-success' : (type === 'danger' ? 'fa-triangle-exclamation text-danger' : 'fa-circle-info text-primary')}"></i>
    <span>${escapeHtml(msg)}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
