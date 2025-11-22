import { Meta, StoryObj } from "@storybook/react";
import Logo from ".";

type Story = StoryObj<typeof Logo>;

const meta: Meta<typeof Logo> = {
    component: Logo,
    title: "Logo",
};
export default meta;

export const Default: Story = {
    args: {},
};
