<script setup>
defineProps({
  flip: { type: Boolean, default: false },
});
</script>

<template>
  <svg
    class="leaf-divider"
    :class="{ flip }"
    viewBox="0 0 400 24"
    preserveAspectRatio="none"
    aria-hidden="true"
  >
    <path
      d="M0,24 C40,4 80,20 120,10 C160,0 200,18 240,8 C280,-2 320,16 360,6 C380,2 390,10 400,4 L400,24 Z"
      fill="currentColor"
    />
  </svg>
</template>

<style scoped>
.leaf-divider {
  display: block;
  width: 100%;
  height: 20px;
  color: var(--surface);
}

.leaf-divider.flip {
  transform: scaleY(-1);
}
</style>
