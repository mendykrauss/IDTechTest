<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getAsset,
  getAssetAudit,
  toggleAsset,
  decommissionAsset,
  deleteAsset,
} from '../api/index.js'
import StatusBadge from '../components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const asset = ref(null)
const loading = ref(true)
const error = ref(null)
const auditHistory = ref([])
const auditLoading = ref(false)
const auditError = ref(null)

const loadAuditHistory = async (assetId) => {
  auditLoading.value = true
  auditError.value = null
  try {
    const data = await getAssetAudit(assetId)
    auditHistory.value = data.history ?? []
  } catch (err) {
    auditError.value = 'Failed to load audit history.'
  } finally {
    auditLoading.value = false
  }
}

const loadAsset = async () => {
  loading.value = true
  error.value = null
  try {
    const loadedAsset = await getAsset(route.params.id)
    asset.value = loadedAsset
    await loadAuditHistory(loadedAsset.id)
  } catch (err) {
    error.value = err.response?.status === 404 ? 'Asset not found.' : 'Failed to load asset.'
  } finally {
    loading.value = false
  }
}

const handleToggle = async () => {
  await toggleAsset(asset.value.id)
  loadAsset()
}

const handleDecommission = async () => {
  if (!confirm('Mark this asset as retired? This should only be done when the device is being removed from service.')) return
  await decommissionAsset(asset.value.id)
  loadAsset()
}

const handleDelete = async () => {
  if (!confirm(`Permanently delete "${asset.value.name}"?`)) return
  await deleteAsset(asset.value.id)
  router.push('/assets')
}

const formatDate = (iso) => {
  if (!iso) return 'Never'
  return new Date(iso).toLocaleString()
}

onMounted(loadAsset)
</script>

<template>
  <div>
    <div class="mb-3">
      <router-link to="/assets" class="text-muted text-decoration-none small">
        <i class="bi bi-arrow-left me-1"></i>Back to Assets
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5 text-muted">
      <div class="spinner-border spinner-border-sm me-2"></div>
      Loading…
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="asset">
      <div class="d-flex align-items-start mb-4 gap-3">
        <div class="flex-grow-1">
          <h1 class="h3 mb-1">{{ asset.name }}</h1>
          <p class="text-muted mb-0">{{ asset.serial_number || 'No serial number recorded' }}</p>
        </div>
        <StatusBadge :status="asset.status" />
      </div>

      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header fw-semibold">Details</div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">Type</span>
                <span class="text-capitalize">{{ asset.asset_type }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">Client</span>
                <router-link :to="`/clients/${asset.client_id}`">{{ asset.client_name }}</router-link>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">Assigned To</span>
                <span>{{ asset.assigned_to || '—' }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">Last Seen</span>
                <span>{{ formatDate(asset.last_seen) }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">Added</span>
                <span>{{ formatDate(asset.created_at) }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header fw-semibold">Notes</div>
            <div class="card-body">
              <p class="mb-0 text-muted" style="white-space: pre-wrap">
                {{ asset.notes || 'No notes recorded.' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-header fw-semibold">Status Change History</div>
        <div class="card-body p-0">
          <div v-if="auditLoading" class="p-3 text-muted small">
            <div class="spinner-border spinner-border-sm me-2"></div>
            Loading audit history...
          </div>

          <div v-else-if="auditError" class="p-3">
            <div class="alert alert-warning mb-0">{{ auditError }}</div>
          </div>

          <div v-else-if="auditHistory.length === 0" class="p-3 text-muted">
            No status changes have been logged yet.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-sm table-striped mb-0 align-middle">
              <thead>
                <tr>
                  <th scope="col">When</th>
                  <th scope="col">From</th>
                  <th scope="col">To</th>
                  <th scope="col">Requester IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in auditHistory" :key="entry.id">
                  <td>{{ formatDate(entry.timestamp) }}</td>
                  <td class="text-capitalize">{{ entry.previous_status }}</td>
                  <td class="text-capitalize">{{ entry.new_status }}</td>
                  <td>{{ entry.requester_ip }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="d-flex gap-2 flex-wrap">
        <button
          v-if="asset.status !== 'retired'"
          class="btn btn-outline-warning"
          @click="handleToggle"
        >
          <i class="bi bi-arrow-repeat me-1"></i>
          {{ asset.status === 'active' ? 'Mark Inactive' : 'Mark Active' }}
        </button>
        <button
          v-if="asset.status !== 'retired'"
          class="btn btn-outline-secondary"
          @click="handleDecommission"
        >
          <i class="bi bi-archive me-1"></i>Decommission
        </button>
        <button class="btn btn-outline-danger ms-auto" @click="handleDelete">
          <i class="bi bi-trash me-1"></i>Delete Asset
        </button>
      </div>
    </div>
  </div>
</template>
