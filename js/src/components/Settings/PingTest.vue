<template>
  <div class="flex justify-between">
    <span>Ping test</span>
    <button type="button" @click="send_ping"
            class="inline-flex items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
      Send ping
    </button>
  </div>
</template>

<script>
export default {
  name: "PingTest",
  data: () => {
    return {}
  },
  methods: {
    send_ping() {
      this.$store.state.websocket_connection.send(JSON.stringify(
          {
            message: "ping"
          }
      ))
      console.log("pong")
    }
  }
}
</script>

<style scoped>

</style>