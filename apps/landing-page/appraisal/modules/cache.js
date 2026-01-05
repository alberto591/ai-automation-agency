// ==================== CACHE MODULE ====================
export const appraisalCache = {
    storage: new Map(),
    ttl: 15 * 60 * 1000,
    generateKey(p) { return `${p.city}_${p.zone}_${p.surface_sqm}_${p.condition}`; },
    get(params) {
        const cached = this.storage.get(this.generateKey(params));
        if (!cached || Date.now() - cached.timestamp > this.ttl) return null;
        return cached.data;
    },
    set(params, data) {
        this.storage.set(this.generateKey(params), { data, timestamp: Date.now() });
    }
};
