<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink> | <RouterLink to="/login">Login</RouterLink> |
    <RouterLink to="/signup">Signup</RouterLink> | <RouterLink to="/products">Search</RouterLink> |
    <RouterLink to="/living-profile">LivingProfile</RouterLink>
  </nav>
  <RouterView></RouterView>
</template>

<style scoped></style>
