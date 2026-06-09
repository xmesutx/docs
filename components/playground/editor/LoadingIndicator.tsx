import { Box, Text } from '@primer/react'

export function LoadingIndicator() {
  return (
    <Box display="flex" flexDirection="column" alignItems="center" py={4}>
      <img width="120px" src="/assets/images/2021/10/playground/loading.gif" alt="bouncing octocat" />
      <Text fontFamily="mono" fontSize={1} color="gray.8">
        Loading...
      </Text>
    </Box>
  )
}
