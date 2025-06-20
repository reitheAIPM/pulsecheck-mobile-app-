import { Builder, builder } from '@builder.io/react'
import { Button } from './src/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './src/components/ui/card'
import { Input } from './src/components/ui/input'
import { Label } from './src/components/ui/label'
import { Textarea } from './src/components/ui/textarea'
import { Badge } from './src/components/ui/badge'
import { Progress } from './src/components/ui/progress'
import { Separator } from './src/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './src/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from './src/components/ui/avatar'
import { Slider } from './src/components/ui/slider'

// Register your components for Builder.io
Builder.registerComponent(Button, {
  name: 'Button',
  inputs: [
    {
      name: 'text',
      type: 'string',
      defaultValue: 'Click me'
    },
    {
      name: 'variant',
      type: 'enum',
      enum: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
      defaultValue: 'default'
    },
    {
      name: 'size',
      type: 'enum',
      enum: ['default', 'sm', 'lg', 'icon'],
      defaultValue: 'default'
    }
  ]
})

Builder.registerComponent(Card, {
  name: 'Card',
  inputs: [
    {
      name: 'title',
      type: 'string',
      defaultValue: 'Card Title'
    },
    {
      name: 'description',
      type: 'string',
      defaultValue: 'Card description'
    },
    {
      name: 'content',
      type: 'string',
      defaultValue: 'Card content goes here'
    }
  ]
})

Builder.registerComponent(Input, {
  name: 'Input',
  inputs: [
    {
      name: 'placeholder',
      type: 'string',
      defaultValue: 'Enter text...'
    },
    {
      name: 'type',
      type: 'enum',
      enum: ['text', 'email', 'password', 'number', 'tel', 'url'],
      defaultValue: 'text'
    }
  ]
})

Builder.registerComponent(Label, {
  name: 'Label',
  inputs: [
    {
      name: 'text',
      type: 'string',
      defaultValue: 'Label'
    }
  ]
})

Builder.registerComponent(Textarea, {
  name: 'Textarea',
  inputs: [
    {
      name: 'placeholder',
      type: 'string',
      defaultValue: 'Enter text...'
    },
    {
      name: 'rows',
      type: 'number',
      defaultValue: 3
    }
  ]
})

Builder.registerComponent(Badge, {
  name: 'Badge',
  inputs: [
    {
      name: 'text',
      type: 'string',
      defaultValue: 'Badge'
    },
    {
      name: 'variant',
      type: 'enum',
      enum: ['default', 'secondary', 'destructive', 'outline'],
      defaultValue: 'default'
    }
  ]
})

Builder.registerComponent(Progress, {
  name: 'Progress',
  inputs: [
    {
      name: 'value',
      type: 'number',
      defaultValue: 50
    },
    {
      name: 'max',
      type: 'number',
      defaultValue: 100
    }
  ]
})

Builder.registerComponent(Separator, {
  name: 'Separator',
  inputs: [
    {
      name: 'orientation',
      type: 'enum',
      enum: ['horizontal', 'vertical'],
      defaultValue: 'horizontal'
    }
  ]
})

Builder.registerComponent(Tabs, {
  name: 'Tabs',
  inputs: [
    {
      name: 'tabs',
      type: 'list',
      subFields: [
        {
          name: 'label',
          type: 'string'
        },
        {
          name: 'content',
          type: 'string'
        }
      ],
      defaultValue: [
        { label: 'Tab 1', content: 'Content 1' },
        { label: 'Tab 2', content: 'Content 2' }
      ]
    }
  ]
})

Builder.registerComponent(Avatar, {
  name: 'Avatar',
  inputs: [
    {
      name: 'src',
      type: 'string',
      defaultValue: ''
    },
    {
      name: 'alt',
      type: 'string',
      defaultValue: 'Avatar'
    },
    {
      name: 'fallback',
      type: 'string',
      defaultValue: 'U'
    }
  ]
})

Builder.registerComponent(Slider, {
  name: 'Slider',
  inputs: [
    {
      name: 'defaultValue',
      type: 'list',
      subFields: [
        {
          name: 'value',
          type: 'number'
        }
      ],
      defaultValue: [{ value: 50 }]
    },
    {
      name: 'max',
      type: 'number',
      defaultValue: 100
    },
    {
      name: 'step',
      type: 'number',
      defaultValue: 1
    }
  ]
})

// Register custom components for your app
Builder.registerComponent(Card, {
  name: 'JournalCard',
  inputs: [
    {
      name: 'title',
      type: 'string',
      defaultValue: 'Journal Entry'
    },
    {
      name: 'content',
      type: 'string',
      defaultValue: 'Today was a great day...'
    },
    {
      name: 'mood',
      type: 'string',
      defaultValue: '😊'
    },
    {
      name: 'date',
      type: 'string',
      defaultValue: '2025-06-20'
    }
  ]
})

// Set up Builder.io configuration
builder.init('93b18bce96bf4218884de91289488848') // Use builder instance instead of Builder class 